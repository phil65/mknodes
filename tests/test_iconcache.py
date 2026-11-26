from typing import TYPE_CHECKING, Any

import pytest

from mknodes.utils import iconcache


if TYPE_CHECKING:
    import pathlib


SVG = '<svg xmlns="http://www.w3.org/2000/svg"><path d="M0"/></svg>'


class FakeFetch:
    """Stand-in for the Iconify API which records the requested icons."""

    def __init__(self) -> None:
        self.calls: list[tuple[str, dict[str, Any]]] = []
        self.fail = False

    def __call__(self, icon: str, **params: Any) -> str:
        self.calls.append((icon, params))
        if self.fail:
            msg = "HTTP Error 429: Too Many Requests"
            raise RuntimeError(msg)
        return SVG.replace("M0", f"M{len(self.calls)}")


@pytest.fixture
def cache_dir(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> pathlib.Path:
    monkeypatch.setenv(iconcache.CACHE_DIR_ENV_VAR, str(tmp_path))
    iconcache._memory_cache.clear()
    yield tmp_path / "icons"
    iconcache._memory_cache.clear()


@pytest.fixture
def fetch(monkeypatch: pytest.MonkeyPatch, cache_dir: pathlib.Path) -> FakeFetch:
    fake = FakeFetch()
    monkeypatch.setattr(iconcache, "_fetch", fake)
    return fake


def _new_process() -> None:
    """Forget the in-memory cache, like a fresh build process would."""
    iconcache._memory_cache.clear()


def test_cache_dir_env_var(cache_dir: pathlib.Path):
    assert iconcache.get_cache_dir() == cache_dir


def test_default_cache_dir(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.delenv(iconcache.CACHE_DIR_ENV_VAR, raising=False)
    path = iconcache.get_cache_dir()
    assert path.name == "icons"
    assert "mknodes" in path.parts


def test_icon_is_fetched_once(fetch: FakeFetch, cache_dir: pathlib.Path):
    first = iconcache.get_icon_svg("mdi:file")
    assert (cache_dir / "mdi" / "file.svg").read_text() == first
    _new_process()
    assert iconcache.get_icon_svg("mdi:file") == first
    assert len(fetch.calls) == 1


def test_equivalent_specs_share_cache_entry(fetch: FakeFetch):
    svg = iconcache.get_icon_svg("mdi:file")
    for spec in ("material/file", ":material-file:"):
        assert iconcache.get_icon_svg(spec) == svg
    assert len(fetch.calls) == 1


def test_params_are_part_of_the_key(fetch: FakeFetch):
    plain = iconcache.get_icon_svg("mdi:file")
    red = iconcache.get_icon_svg("mdi:file", color="red")
    big = iconcache.get_icon_svg("mdi:file", height=48)
    assert len({plain, red, big}) == 3  # noqa: PLR2004
    assert iconcache.get_icon_svg("mdi:file", color="red") == red
    assert len(fetch.calls) == 3  # noqa: PLR2004
    assert fetch.calls[1][1]["color"] == "red"


def test_multiple_icons(fetch: FakeFetch):
    svg = iconcache.get_icon_svg("mdi:file|mdi:folder")
    assert svg.count("<svg") == 2  # noqa: PLR2004
    _new_process()
    assert iconcache.get_icon_svg("mdi:folder|mdi:file").count("<svg") == 2  # noqa: PLR2004
    assert len(fetch.calls) == 2  # noqa: PLR2004


def test_network_failure_with_cached_copy(fetch: FakeFetch):
    svg = iconcache.get_icon_svg("mdi:file")
    _new_process()
    fetch.fail = True
    assert iconcache.get_icon_svg("mdi:file") == svg
    assert len(fetch.calls) == 1


def test_network_failure_without_cached_copy(fetch: FakeFetch):
    fetch.fail = True
    with pytest.raises(RuntimeError, match="429"):
        iconcache.get_icon_svg("mdi:file")


def test_unresolvable_specs_are_cached_without_network(fetch: FakeFetch):
    # Needs the Iconify collection list to resolve its prefix, so it is keyed as-is.
    svg = iconcache.get_icon_svg(":fa-brands-github:")
    _new_process()
    fetch.fail = True
    assert iconcache.get_icon_svg(":fa-brands-github:") == svg


def test_invalid_cache_file_is_refetched(fetch: FakeFetch):
    path = iconcache.get_cache_path("mdi:file")
    path.parent.mkdir(parents=True)
    path.write_text("Too Many Requests")
    assert iconcache.get_icon_svg("mdi:file").startswith("<svg")
    assert len(fetch.calls) == 1
    assert path.read_text().startswith("<svg")


def test_invalid_response_is_not_cached(fetch: FakeFetch, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(iconcache, "_fetch", lambda icon, **kw: "404")
    assert iconcache.get_icon_svg("mdi:nonexistent") == "404"
    assert not iconcache.get_cache_path("mdi:nonexistent").exists()


def test_clear_icon_cache(fetch: FakeFetch, cache_dir: pathlib.Path):
    iconcache.get_icon_svg("mdi:file")
    assert cache_dir.exists()
    iconcache.clear_icon_cache()
    assert not cache_dir.exists()
    iconcache.get_icon_svg("mdi:file")
    assert len(fetch.calls) == 2  # noqa: PLR2004


def test_jinja_filter_uses_cache(fetch: FakeFetch):
    import jinjarope

    env = jinjarope.Environment()
    first = env.render_string("{{ 'mdi:file' | get_icon_svg }}")
    _new_process()
    assert env.render_string("{{ 'material/file' | get_icon_svg }}") == first
    assert len(fetch.calls) == 1


def test_mkicon_uses_cache(fetch: FakeFetch):
    import mknodes as mk

    svg = mk.MkIcon("mdi:file").svg
    _new_process()
    fetch.fail = True
    assert mk.MkIcon("mdi:file").svg == svg


def _bridged_fetch(icon: str, **params: Any) -> str:
    """Fetch like pycons does: a coroutine run via anyenv's sync bridge."""
    from anyenv import run_sync

    async def get_bytes() -> str:
        return SVG

    return run_sync(get_bytes())


@pytest.mark.parametrize("use_async", [False, True])
def test_fetch_inside_running_loop(
    monkeypatch: pytest.MonkeyPatch, cache_dir: pathlib.Path, use_async: bool
):
    # Builds run inside anyenv.run_sync. Its context carries anyio's "current async
    # library" marker, which made the nested sync fetch fail ("Could not find icon",
    # "coroutine 'get_bytes' was never awaited") on a cold icon cache.
    from anyenv import run_sync

    import mknodes as mk

    monkeypatch.setattr(iconcache, "_fetch_unisolated", _bridged_fetch)

    async def render() -> str:
        if use_async:
            return await mk.MkIcon("mdi:file").to_markdown()
        return iconcache.get_icon_svg("mdi:file")

    assert run_sync(render()) == SVG
    assert iconcache.get_cache_path("mdi:file").read_text() == SVG


async def test_async_icon_is_fetched_once(fetch: FakeFetch):
    first = await iconcache.get_icon_svg_async("mdi:file|mdi:folder")
    _new_process()
    assert await iconcache.get_icon_svg_async("mdi:file|mdi:folder") == first
    assert iconcache.get_icon_svg("mdi:folder") == first[len(first) // 2 :]
    assert len(fetch.calls) == 2  # noqa: PLR2004
