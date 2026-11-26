"""Inputs store: resolve phase, lock file, offline / refresh modes, migrated nodes."""

import asyncio
import json
import pathlib
from typing import Any, ClassVar

import pytest

import mknodes as mk
from mknodes import inputs
from mknodes.build import DocBuilder
from mknodes.info import contexts
from mknodes.inputs import InputRequest, InputStore, MissingInputError
from mknodes.utils import diagnostics, iconcache


SVG = '<svg xmlns="http://www.w3.org/2000/svg"><path d="M0"/></svg>'


class FakeKind(inputs.InputKind):
    """Locked kind returning "value-<key>", counting fetches (concurrency too)."""

    name = "fake"
    source = "tests"
    calls: ClassVar[list[str]] = []
    active = 0
    max_active = 0

    async def fetch(self, params: dict[str, Any]) -> str:
        cls = type(self)
        cls.calls.append(params["key"])
        cls.active += 1
        cls.max_active = max(cls.max_active, cls.active)
        await asyncio.sleep(0.01)
        cls.active -= 1
        if params["key"] == "broken":
            msg = "boom"
            raise ValueError(msg)
        return f"value-{params['key']}"


class LocalKind(FakeKind):
    """Unlocked kind (like git data): never written to the lock file."""

    name = "local"
    locked = False


@pytest.fixture
def fake_kinds(monkeypatch: pytest.MonkeyPatch) -> type[FakeKind]:
    monkeypatch.setitem(inputs.KINDS, "fake", FakeKind())
    monkeypatch.setitem(inputs.KINDS, "local", LocalKind())
    FakeKind.calls = []
    FakeKind.active = FakeKind.max_active = 0
    return FakeKind


@pytest.fixture
def no_network(monkeypatch: pytest.MonkeyPatch) -> None:
    """Make every network fetch fail (icons, licenses, LLM)."""

    def fail(*_args: object, **_kwargs: object) -> Any:
        msg = "network access in a test"
        raise AssertionError(msg)

    async def afail(*_args: object, **_kwargs: object) -> Any:
        fail()

    monkeypatch.setattr(iconcache, "_fetch", fail)
    monkeypatch.setattr(iconcache, "fetch_icon_prefixes", fail)
    monkeypatch.setattr("anyenv.get_json", afail)
    monkeypatch.setattr("anyenv.get_bytes", afail)
    monkeypatch.setattr("mknodes.templatenodes.mkllm.complete_llm", afail)


def _requests(*keys: str, kind: str = "fake") -> list[InputRequest]:
    return [InputRequest.create(kind, key=k) for k in keys]


async def test_resolve_is_concurrent_bounded_and_deduplicated(fake_kinds: type[FakeKind]):
    store = InputStore(max_concurrency=3)
    await store.resolve(_requests(*"abcdefgh", "a", "b"))
    assert sorted(fake_kinds.calls) == list("abcdefgh")
    assert fake_kinds.max_active == 3  # noqa: PLR2004
    assert store.get("fake", key="c") == "value-c"
    await store.resolve(_requests("a"))  # already resolved: no fetch
    assert len(fake_kinds.calls) == 8  # noqa: PLR2004
    assert store.stats()["fetched"] == 8  # noqa: PLR2004


async def test_lock_file_round_trip(fake_kinds: type[FakeKind], tmp_path: pathlib.Path):
    lock = tmp_path / "mknodes.lock"
    store = InputStore(lock)
    await store.resolve([*_requests("b", "a"), *_requests("x", kind="local")])
    assert store.save()
    assert not store.save()  # unchanged: not written again
    data = json.loads(lock.read_text())
    assert data["version"] == 1
    assert list(data["inputs"]) == ["fake"]  # unlocked kinds are not written
    assert list(data["inputs"]["fake"]) == ['{"key":"a"}', '{"key":"b"}']
    entry = data["inputs"]["fake"]['{"key":"a"}']
    assert entry["value"] == "value-a"
    assert entry["source"] == "tests"
    assert entry["fetched_at"].endswith("Z")
    assert lock.read_text() == store.dumps()  # deterministic, sorted

    fake_kinds.calls.clear()
    reloaded = InputStore(lock)
    await reloaded.resolve(_requests("a", "b"))
    assert reloaded.get("fake", key="b") == "value-b"
    assert fake_kinds.calls == []


async def test_live_mode_adds_without_pruning(fake_kinds: type[FakeKind], tmp_path):
    lock = tmp_path / "mknodes.lock"
    first = InputStore(lock)
    await first.resolve(_requests("a"))
    first.save()
    second = InputStore(lock)
    await second.resolve(_requests("b"))
    second.save()
    assert set(json.loads(lock.read_text())["inputs"]["fake"]) == {
        '{"key":"a"}',
        '{"key":"b"}',
    }


async def test_refresh_refetches_and_prunes(fake_kinds: type[FakeKind], tmp_path):
    lock = tmp_path / "mknodes.lock"
    store = InputStore(lock)
    await store.resolve(_requests("a", "b"))
    store.save()
    fake_kinds.calls.clear()
    refresh = InputStore(lock, mode="refresh")
    await refresh.resolve(_requests("a"))
    assert fake_kinds.calls == ["a"]
    assert refresh.get("fake", key="a") == "value-a"
    refresh.save()
    assert list(json.loads(lock.read_text())["inputs"]["fake"]) == ['{"key":"a"}']


async def test_offline_missing_input_is_an_error(fake_kinds: type[FakeKind], tmp_path):
    lock = tmp_path / "mknodes.lock"
    store = InputStore(lock)
    await store.resolve(_requests("a"))
    store.save()
    text = lock.read_text()

    offline = InputStore(lock, mode="offline")
    with pytest.raises(MissingInputError) as exc:
        await offline.resolve(_requests("a", "b", "c"))
    assert exc.value.missing == [("fake", '{"key":"b"}'), ("fake", '{"key":"c"}')]
    assert 'fake: {"key":"b"}' in str(exc.value)
    assert "--offline" in str(exc.value)
    with pytest.raises(MissingInputError):
        offline.get("fake", key="b")
    with pytest.raises(MissingInputError):
        await offline.aget("fake", key="b")
    assert offline.get("fake", key="a") == "value-a"
    # Unlocked (local) inputs are computed offline as well.
    await offline.resolve(_requests("x", kind="local"))
    assert offline.get("local", key="x") == "value-x"
    assert not offline.save()
    assert lock.read_text() == text


async def test_failed_fetch_is_remembered(fake_kinds: type[FakeKind]):
    store = InputStore()
    await store.resolve(_requests("broken", "ok"))
    with pytest.raises(ValueError, match="boom"):
        store.get("fake", key="broken")
    assert fake_kinds.calls.count("broken") == 1
    assert store.get("fake", key="ok") == "value-ok"


def test_unknown_kind():
    with pytest.raises(KeyError, match="Unknown input kind"):
        InputStore().get("nope", key="x")


def test_icon_key_ids():
    kind = inputs.get_kind("icon")
    assert kind.key_id({"icon": "mdi:file", "color": None, "box": False}) == "mdi:file"
    params = {"icon": "mdi:file", "rotate": 90, "color": "red"}
    assert kind.key_id(params) == "mdi:file?color=red&rotate=90"


def _offline_ctx(
    tmp_path: pathlib.Path, data: dict[str, dict[str, Any]]
) -> contexts.ProjectContext:
    lock = tmp_path / "mknodes.lock"
    entries = {
        kind: {
            key: {"fetched_at": "2026-11-26T00:00:00Z", "source": "tests", "value": value}
            for key, value in items.items()
        }
        for kind, items in data.items()
    }
    lock.write_text(json.dumps({"inputs": entries, "version": 1}))
    return contexts.ProjectContext(inputs=InputStore(lock, mode="offline"))


async def test_migrated_nodes_render_from_lock_without_network(no_network, tmp_path):
    llm = mk.MkLlm("Say hi", model="test:model")
    llm_key = inputs.get_kind("llm").key_id(llm._llm_params())
    ctx = _offline_ctx(
        tmp_path,
        {
            "icon": {"mdi:file": SVG, "mdi:file?color=red": SVG.replace("M0", "M1")},
            "license": {"mit": {"content": "MIT license text", "name": "MIT"}},
            "llm": {llm_key: "Hi from the lock file"},
        },
    )
    page = mk.MkPage(context=ctx)
    icon = mk.MkIcon("mdi:file")
    page += icon
    page += mk.MkIcon("mdi:file", color="red")
    page += mk.MkLicense("MIT")
    page += llm
    md = await page.to_markdown()
    assert SVG in md
    assert "M1" in md
    assert "MIT license text" in md
    assert "Hi from the lock file" in md
    assert icon.svg == SVG  # sync access


async def test_migrated_node_missing_offline_is_an_error(no_network, tmp_path):
    ctx = _offline_ctx(tmp_path, {"icon": {}})
    with pytest.raises(MissingInputError):
        await mk.MkIcon("mdi:folder", context=ctx).to_markdown()


async def test_mkllm_offline_without_agentpool_uses_placeholder(monkeypatch, tmp_path):
    """Offline, a text which is not locked can't be fetched without agentpool: placeholder."""
    from mknodes.templatenodes import mkllm

    monkeypatch.setattr(inputs.get_kind("llm"), "available", lambda: False)
    ctx = _offline_ctx(tmp_path, {"llm": {}})
    page = mk.MkPage(context=ctx)
    llm = mk.MkLlm("Say hi")
    page += llm
    await DocBuilder().build(_nav_with(page, ctx))  # no MissingInputError
    assert await llm.to_markdown() == mkllm.UNAVAILABLE_TEXT


def test_pyconify_key_reads_icon_prefixes_from_the_store(no_network, tmp_path):
    """Specs with a prefix need no lookup, others use the locked icon set prefixes."""
    store = _offline_ctx(tmp_path, {"icon_prefixes": {}}).inputs
    with inputs.use_store(store):
        # no lookup needed: no MissingInputError although the prefixes are not locked
        assert iconcache.get_pyconify_key("mdi:file") == "mdi:file"
        assert iconcache.get_pyconify_key("material/file") == "mdi:file"
        assert iconcache.get_pyconify_key(":material-file:") == "mdi:file"
        with pytest.raises(MissingInputError):
            iconcache.get_pyconify_key(":fa-brands-github:")
    lock = {"icon_prefixes": {"collections": ["fa", "fa-brands", "mdi"]}}
    with inputs.use_store(_offline_ctx(tmp_path, lock).inputs):
        assert iconcache.get_pyconify_key(":fa-brands-github:") == "fa-brands:github"
        assert iconcache.get_pyconify_key("fa-check") == "fa:check"
        assert iconcache.get_pyconify_key("folder") == "mdi:folder"


async def test_github_flavour_icon_offline(no_network, tmp_path):
    """The GitHub flavour's icon `<img>` URLs need no network with a lock file."""
    lock = {"icon_prefixes": {"collections": ["fa-brands", "mdi"]}}
    ctx = _offline_ctx(tmp_path, lock)
    with inputs.use_store(ctx.inputs):
        md = await mk.MkIcon(":fa-brands-github:", context=ctx).to_markdown(flavor="github")
    assert "https://api.iconify.design/fa-brands/github.svg" in md


async def test_mkinclude_url_from_lock_without_network(no_network, tmp_path):
    url = "https://example.com/README.md"
    ctx = _offline_ctx(tmp_path, {"file": {url: "# Included from the lock"}})
    node = mk.MkInclude(url, context=ctx)
    assert node.get_input_requests() == [InputRequest.create("file", url=url)]
    assert "Included from the lock" in await node.to_markdown()
    local = tmp_path / "local.md"
    local.write_text("local text")
    assert mk.MkInclude(str(local), context=ctx).get_input_requests() == []
    assert await mk.MkInclude(str(local), context=ctx).to_markdown() == "local text"


def _nav_with(page: mk.MkPage, ctx: contexts.ProjectContext) -> mk.MkNav:
    nav = mk.MkNav(context=ctx)
    nav += page
    return nav


async def test_builder_resolves_inputs_before_rendering(fake_kinds, monkeypatch):
    """The DocBuilder resolves all requested inputs concurrently, nodes read them."""
    fetched: list[str] = []

    async def fake_fetch(icon: str, **_params: Any) -> str:
        fetched.append(icon)
        await asyncio.sleep(0.01)
        return SVG.replace("M0", icon)

    monkeypatch.setattr(iconcache, "fetch_icon_svg_async", fake_fetch)
    ctx = contexts.ProjectContext(inputs=InputStore())
    nav = mk.MkNav(context=ctx)
    page = nav.add_page("Icons", is_index=True)
    for name in ("mdi:a", "mdi:b", "mdi:c", "mdi:a"):
        page += mk.MkIcon(name)
    output = await DocBuilder().build(nav)
    assert sorted(fetched) == ["mdi:a", "mdi:b", "mdi:c"]
    assert ctx.inputs.on_demand == set()  # all came from the resolve phase
    assert "mdi:b" in output.pages["index.md"]


def test_icon_helpers_use_the_active_store(monkeypatch: pytest.MonkeyPatch):
    """Code without a node context (themes, emoji index) reads the build's store."""
    monkeypatch.setattr(iconcache, "_fetch", lambda *_a, **_kw: pytest.fail("fetched"))
    store = InputStore()
    store.entries["icon", "mdi:file"] = inputs.InputEntry(SVG, "", "tests")
    assert inputs.active_store() is None
    with inputs.use_store(store):
        assert inputs.active_store() is store
        assert iconcache.get_icon_svg("mdi:file") == SVG
        assert asyncio.run(iconcache.get_icon_svg_async("mdi:file")) == SVG
    assert inputs.active_store() is None
    assert ("icon", "mdi:file") in store.used


ICON_BUILD = """\
import mknodes as mk


def build(root, theme):
    page = root.add_page("Intro", is_index=True)
    page += mk.MkIcon("mdi:file")
"""


def test_cli_lock_file_and_offline(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch):
    from typer.testing import CliRunner

    from mknodes import cli

    (tmp_path / "build.py").write_text(ICON_BUILD)
    repo = pathlib.Path(__file__).parents[1].as_posix()
    (tmp_path / "mkdocs.yml").write_text(
        "site_name: Fixture\nplugins:\n  - mknodes:\n      build_fn: build.py:build\n"
        f"      repo_path: {repo}\n"
    )
    (tmp_path / "docs").mkdir()
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv(iconcache.CACHE_DIR_ENV_VAR, str(tmp_path / "cache"))
    monkeypatch.setattr(iconcache, "_fetch", lambda *_a, **_kw: SVG)
    # Material: the GitHub flavour resolves icon prefixes via the Iconify collection list.
    args = ["generate", "--engine", "markdown", "--flavor", "material", "--generated-dir", "out"]
    runner = CliRunner()

    result = runner.invoke(cli.cli, args)
    assert result.exit_code == 0, result.output
    lock = json.loads((tmp_path / "mknodes.lock").read_text())
    assert lock["inputs"]["icon"]["mdi:file"]["value"] == SVG
    assert SVG in (tmp_path / "out" / "index.md").read_text()

    monkeypatch.setattr(iconcache, "_fetch", lambda *_a, **_kw: pytest.fail("network"))
    iconcache.clear_icon_cache()
    result = runner.invoke(cli.cli, [*args, "--offline"])
    assert result.exit_code == 0, result.output

    # Another file: the build script module stays imported.
    (tmp_path / "build2.py").write_text(ICON_BUILD.replace("mdi:file", "mdi:folder"))
    result = runner.invoke(cli.cli, [*args, "--offline", "--build-fn", "build2.py:build"])
    assert result.exit_code == 1
    assert "icon: mdi:folder" in result.output
    assert "missing from the lock file" in result.output


async def test_remote_files_go_through_the_store(no_network, tmp_path, monkeypatch):
    """Remote files (any fsspec protocol) are `file` / `binary_file` inputs, local ones not."""
    import base64

    from mknodes.inputs import kinds
    from mknodes.utils import pathhelpers

    files = {
        "memory://inputs/page.md": b"# Remote page\n\ntext",
        "memory://inputs/image.png": b"\x89PNG-bytes",
    }

    async def fake_fetch(url: str) -> bytes:
        return files[url]

    monkeypatch.setattr(kinds, "_fetch_bytes", fake_fetch)
    store = InputStore()
    with inputs.use_store(store):
        await store.resolve([
            InputRequest.create("file", url="memory://inputs/page.md"),
            InputRequest.create("binary_file", url="memory://inputs/image.png"),
        ])
        files.clear()  # from now on only the store has them
        assert pathhelpers.load_file("memory://inputs/page.md").startswith("# Remote page")
        assert mk.MkText.from_url("memory://inputs/page.md#Remote page") is not None
        image = mk.MkBinaryImage.for_file("memory://inputs/image.png")
        assert image.data == b"\x89PNG-bytes"
        from mknodes.extranodes.mkcodeimage import MkCodeImage

        code = MkCodeImage.for_file("memory://inputs/page.md")
        assert code.title == "page.md"
    assert store.entries["binary_file", "memory://inputs/image.png"].value == (
        base64.b64encode(b"\x89PNG-bytes").decode()
    )
    assert pathhelpers.is_remote("https://example.com/a.md")
    assert pathhelpers.is_remote("github://phil65:mknodes@main/README.md")
    assert not pathhelpers.is_remote("docs/index.md")
    assert not pathhelpers.is_remote("file:///tmp/x.md")
    assert not pathhelpers.is_remote(r"C:\docs\x.md")
    local = tmp_path / "local.md"
    local.write_bytes(b"line\r\n")
    assert pathhelpers.load_file(local) == "line\r\n"


async def test_jinja_load_file_reads_remote_files_from_the_store(no_network, tmp_path):
    url = "https://example.com/snippet.md"
    ctx = _offline_ctx(tmp_path, {"file": {url: "snippet from the lock"}})
    with inputs.use_store(ctx.inputs):
        node = mk.MkText(f"{{{{ '{url}' | load_file }}}}", render_jinja=True, context=ctx)
        assert await node.to_markdown() == "snippet from the lock"


async def test_mkpydeps_and_mkcommandoutput_run_in_the_resolve_phase(monkeypatch):
    """Pydeps / shell commands are unlocked inputs: computed before rendering."""
    from jinjarope import envglobals

    from mknodes.templatenodes import mkpydeps

    calls: list[str] = []

    def fake_svg(folder_name: str, **_kwargs: Any) -> str:
        calls.append(f"pydeps {folder_name}")
        return "<svg>deps</svg>"

    def fake_call(call: str, cwd: str | None = None, use_cache: bool = False) -> str:
        calls.append(f"run {call}")
        return "command output"

    monkeypatch.setattr(mkpydeps, "get_dependency_svg", fake_svg)
    monkeypatch.setattr(envglobals, "get_output_from_call", fake_call)
    ctx = contexts.ProjectContext(inputs=InputStore())
    nav = mk.MkNav(context=ctx)
    page = nav.add_page("Tools", is_index=True)
    page += mk.MkPyDeps("src/mknodes", max_bacon=1)
    page += mk.MkCommandOutput(["mytool", "--help"])
    page += mk.MkText("{{ ['other', '--version'] | check_output }}", render_jinja=True)
    output = await DocBuilder().build(nav)
    md = output.pages["index.md"]
    assert "<svg>deps</svg>" in md
    assert md.count("command output") == 2  # noqa: PLR2004
    assert sorted(calls) == ["pydeps src/mknodes", "run mytool --help", "run other --version"]
    assert {kind for kind, _ in ctx.inputs.fetched} == {"pydeps", "command"}
    assert ctx.inputs.to_lock_data()["inputs"] == {}  # unlocked: not in the lock file


def test_license_text_without_license_file_comes_from_the_store(monkeypatch, tmp_path):
    from mknodes.info import folderinfo

    store = InputStore()
    store.entries["license", "mit"] = inputs.InputEntry({"content": "MIT text"}, "", "tests")
    info = folderinfo.FolderInfo(pathlib.Path(__file__).parents[1])
    monkeypatch.setattr(folderinfo.FolderInfo, "license_file_path", None)
    monkeypatch.setattr(type(info.info), "license_name", property(lambda _self: "MIT"))
    with inputs.use_store(store):
        assert info.license_text == "MIT text"


def test_build_time_is_fixed_and_honours_source_date_epoch(monkeypatch):
    from mknodes.utils import buildtime

    monkeypatch.setenv("SOURCE_DATE_EPOCH", "1700000000")
    buildtime.build_time.cache_clear()
    try:
        assert buildtime.build_time().year == 2023  # noqa: PLR2004
        assert buildtime.utcnow() == buildtime.build_time()
        node = mk.MkText("{{ utcnow().year }}", render_jinja=True)
        assert node.to_markdown_sync() == "2023"
    finally:
        buildtime.build_time.cache_clear()


@pytest.fixture
def io_guard(monkeypatch: pytest.MonkeyPatch) -> list[str]:
    """Record network / subprocess / fetch calls made inside a render pass."""
    import socket
    import subprocess

    violations: list[str] = []

    def guard(name: str, fn: Any) -> Any:
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            if inputs.current_pass() is not None:
                violations.append(name)
            return fn(*args, **kwargs)

        return wrapper

    monkeypatch.setattr(socket.socket, "connect", guard("connect", socket.socket.connect))
    monkeypatch.setattr(
        subprocess.Popen, "__init__", guard("subprocess", subprocess.Popen.__init__)
    )
    for kind in inputs.KINDS.values():
        monkeypatch.setattr(kind, "fetch", guard(f"fetch {kind.name}", kind.fetch))
        monkeypatch.setattr(kind, "fetch_sync", guard(f"fetch {kind.name}", kind.fetch_sync))
    return violations


async def test_rendering_does_no_io(io_guard: list[str], monkeypatch: pytest.MonkeyPatch):
    """Inputs only known while rendering (templates) get resolved between render passes."""
    from mknodes.inputs import kinds

    monkeypatch.setattr(iconcache, "_fetch", lambda icon, **_kw: SVG.replace("M0", icon))

    async def fake_bytes(url: str) -> bytes:
        return f"text of {url}".encode()

    monkeypatch.setattr(kinds, "_fetch_bytes", fake_bytes)
    ctx = contexts.ProjectContext(inputs=InputStore())
    nav = mk.MkNav(context=ctx)
    page = nav.add_page("Index", is_index=True)
    page += mk.MkIcon("mdi:declared")  # declared: resolve phase
    # Only known while rendering: page Jinja pass, template node, filters.
    page += "{{ 'mdi:in-page-pass' | MkIcon }}"
    page += mk.MkText(
        "{{ 'mdi:in-template' | MkIcon }} {{ 'https://example.com/x.md' | load_file }}"
        " {{ 'echo from-shell' | check_output }}",
        render_jinja=True,
    )
    page += mk.MkCommandOutput(["echo", "declared-command"])
    with diagnostics.collect() as collected:
        output = await DocBuilder().build(nav)
    md = output.pages["index.md"]
    for icon in ("mdi:declared", "mdi:in-page-pass", "mdi:in-template"):
        assert SVG.replace("M0", icon) in md
    assert "text of https://example.com/x.md" in md
    assert "from-shell" in md
    assert "declared-command" in md
    assert io_guard == []
    assert ctx.inputs.on_demand == set()
    assert list(collected) == []


async def test_render_passes_discard_diagnostics_of_retried_renders(monkeypatch):
    """A render which read a missing input is discarded with what it reported."""
    monkeypatch.setattr(iconcache, "_fetch", lambda icon, **_kw: SVG)
    ctx = contexts.ProjectContext(inputs=InputStore())
    node = mk.MkText("{{ 'mdi:x' | MkIcon }}", render_jinja=True, context=ctx)
    calls: list[bool] = []

    def flaky_render() -> str:
        has_icon = ("icon", "mdi:x") in ctx.inputs.entries
        calls.append(has_icon)
        if not has_icon:
            diagnostics.report("node", "broken while the icon is missing")
        return node.to_markdown_sync()

    with diagnostics.collect() as collected:
        md = inputs.run_passes(flaky_render)
    assert SVG in md
    assert calls == [False, True]
    assert list(collected) == []
    with inputs.render_pass() as render, pytest.raises(inputs.InputPendingError):
        ctx.inputs.get("icon", icon="mdi:other")
    assert render.requests()[0][1] == [InputRequest.create("icon", icon="mdi:other")]


def test_str_of_a_node_resolves_its_inputs_first(io_guard, monkeypatch):
    """Top-level `str(node)` / `to_markdown_sync()` run render passes too."""
    monkeypatch.setattr(iconcache, "_fetch", lambda icon, **_kw: SVG)
    node = mk.MkText("{{ 'mdi:y' | MkIcon }}", render_jinja=True)
    assert SVG in str(node)
    assert io_guard == []
