"""Inputs store: resolve phase, lock file, offline / refresh modes, migrated nodes."""

from __future__ import annotations

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
from mknodes.utils import iconcache


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
    monkeypatch.setattr("anyenv.get_json", afail)
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
