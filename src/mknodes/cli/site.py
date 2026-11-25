"""Site generator commands: build, serve, generate."""

from __future__ import annotations

import contextlib
import pathlib
import signal
import subprocess
from typing import TYPE_CHECKING, Any

import typer as t

from mknodes.cli.app import REPO_CMDS, REPO_HELP, cli, quiet_option, verbose_option
from mknodes.site import paths, watch as watch_
from mknodes.site.settings import GeneratorSettings
from mknodes.utils import log


if TYPE_CHECKING:
    from mknodes.site.writers import Writer


logger = log.get_logger(__name__)

BUILD_HELP = "Path to the build script. (form: `path.to.module:function` )"
SITE_DIR_HELP = "Path to the folder where the HTML should get written."
DEPTH_HELP = "Git clone depth in case repository is remote. Important for changelog generation."
CFG_PATH_HELP = "Path to the config file."
STRICT_HELP = "Strict mode (fails on warnings)"
ENGINE_HELP = "Site engine: `zensical` (HTML site, default) or `markdown` (plain Markdown files)."
FLAVOR_HELP = "Markdown flavour (`material`, `github`). Default: the engine's flavour."
WATCH_HELP = "Keep running and regenerate when project sources change."
GEN_DIR_HELP = "Folder for generated pages (default: the docs dir)."
SITE_DIR_CMDS = "-d", "--site-dir"
BUILD_CMS = "-b", "--build-fn"
DEPTH_CMDS = "-c", "--clone-depth"
CFG_PATH_CMDS = "-p", "--config-path"
STRICT_CMDS = "-s", "--strict"
ENGINE_CMDS = "-e", "--engine"
FLAVOR_CMDS = ("--flavor",)
DEFAULT_ENGINE = "zensical"


def check_engine(value: str) -> str:
    """Only accept engines with a writer."""
    from mknodes.site.writers import WRITERS

    if value not in WRITERS:
        msg = (
            f"Unsupported engine {value!r} (available: {', '.join(WRITERS)}). "
            "Zensical builds HTML sites, `markdown` writes plain Markdown files."
        )
        raise t.BadParameter(msg)
    return value


def _engine_option() -> Any:
    return t.Option(DEFAULT_ENGINE, *ENGINE_CMDS, help=ENGINE_HELP, callback=check_engine)


@cli.command()
def build(
    repo_path: str = t.Option(None, *REPO_CMDS, help=REPO_HELP, show_default=False),
    build_fn: str = t.Option(None, *BUILD_CMS, help=BUILD_HELP, show_default=False),
    site_dir: str = t.Option(None, *SITE_DIR_CMDS, help=SITE_DIR_HELP, show_default=False),
    clone_depth: int = t.Option(None, *DEPTH_CMDS, help=DEPTH_HELP, show_default=False),
    config_path: str = t.Option(paths.CFG_DEFAULT, *CFG_PATH_CMDS, help=CFG_PATH_HELP),
    strict: bool = t.Option(False, *STRICT_CMDS, help=STRICT_HELP),
    engine: str = _engine_option(),
    flavor: str = t.Option(None, *FLAVOR_CMDS, help=FLAVOR_HELP, show_default=False),
    _verbose: bool = verbose_option(),
    _quiet: bool = quiet_option(),
):
    """Build a MkNodes-based website, locally or remotely.

    Runs the build function on given repository (either locally or a hosted one),
    writes the generated pages and config (see `generate`) and builds the HTML website
    with `zensical build -f <generated config>`.

    Further info here: https://phil65.github.io/mknodes/CLI/
    """
    settings = _load_settings(
        config_path=config_path,
        build_fn=build_fn,
        repo_path=repo_path,
        clone_depth=clone_depth,
        site_dir=site_dir,
        flavor=flavor,
    )
    writer = _generate(settings, engine)
    args = ["--strict"] if strict else []
    if (cmd := writer.build_command(extra_args=args)) is None:
        return  # no build step, the generated files are the result
    raise t.Exit(subprocess.call(cmd))


@cli.command()
def serve(
    repo_path: str = t.Option(None, *REPO_CMDS, help=REPO_HELP, show_default=False),
    build_fn: str = t.Option(None, *BUILD_CMS, help=BUILD_HELP, show_default=False),
    clone_depth: int = t.Option(None, *DEPTH_CMDS, help=DEPTH_HELP, show_default=False),
    config_path: str = t.Option(paths.CFG_DEFAULT, *CFG_PATH_CMDS, help=CFG_PATH_HELP),
    engine: str = _engine_option(),
    flavor: str = t.Option(None, *FLAVOR_CMDS, help=FLAVOR_HELP, show_default=False),
    _verbose: bool = verbose_option(),
    _quiet: bool = quiet_option(),
):
    """Serve a MkNodes-based website, locally or remotely.

    This is `mknodes generate --watch` running next to
    `zensical serve -f <generated config>` (serves on http://localhost:8000/).

    Further info here: https://phil65.github.io/mknodes/CLI/
    """
    opts: dict[str, Any] = dict(
        config_path=config_path,
        build_fn=build_fn,
        repo_path=repo_path,
        clone_depth=clone_depth,
        flavor=flavor,
    )
    settings = _load_settings(**opts)
    writer = _generate(settings, engine)
    if (cmd := writer.build_command(serve=True)) is None:
        msg = f"Engine {engine!r} has no server. Use `generate --watch` instead."
        raise t.BadParameter(msg)
    process = subprocess.Popen(cmd)
    signal.signal(signal.SIGTERM, _raise_keyboard_interrupt)
    try:
        watch_.watch(
            settings,
            watch_.regenerate_in_subprocess(_generate_args(engine=engine, **opts)),
            should_stop=lambda: process.poll() is not None,
        )
    except KeyboardInterrupt:
        pass
    finally:
        if process.poll() is None:
            process.terminate()
            process.wait()
    raise t.Exit(process.returncode or 0)


@cli.command()
def generate(
    repo_path: str = t.Option(None, *REPO_CMDS, help=REPO_HELP, show_default=False),
    build_fn: str = t.Option(None, *BUILD_CMS, help=BUILD_HELP, show_default=False),
    clone_depth: int = t.Option(None, *DEPTH_CMDS, help=DEPTH_HELP, show_default=False),
    config_path: str = t.Option(paths.CFG_DEFAULT, *CFG_PATH_CMDS, help=CFG_PATH_HELP),
    engine: str = _engine_option(),
    flavor: str = t.Option(None, *FLAVOR_CMDS, help=FLAVOR_HELP, show_default=False),
    generated_dir: str = t.Option(None, "--generated-dir", help=GEN_DIR_HELP),
    watch: bool = t.Option(False, "-w", "--watch", help=WATCH_HELP),
    _verbose: bool = verbose_option(),
    _quiet: bool = quiet_option(),
):
    """Generate the site input (pages, nav, assets, config) for the site engine.

    Runs the build function (`mknodes.site:parse` / the default website unless
    configured in `[tool.mknodes]` of `pyproject.toml` or in the `mknodes` entry of the
    `plugins` list of `mkdocs.yml`) and writes the generated pages into the docs dir plus
    a generated config (`mkdocs.generated.yml`) inheriting from `mkdocs.yml`.
    Build afterwards with `zensical build -f mkdocs.generated.yml`.
    """
    opts: dict[str, Any] = dict(
        config_path=config_path,
        build_fn=build_fn,
        repo_path=repo_path,
        clone_depth=clone_depth,
        generated_dir=generated_dir,
        flavor=flavor,
    )
    settings = _load_settings(**opts)
    _generate(settings, engine)
    if watch:
        regenerate = watch_.regenerate_in_subprocess(_generate_args(engine=engine, **opts))
        with contextlib.suppress(KeyboardInterrupt):
            watch_.watch(settings, regenerate)


def _raise_keyboard_interrupt(*_args: Any) -> None:
    raise KeyboardInterrupt


def _load_settings(
    config_path: str | None,
    build_fn: str | None = None,
    repo_path: str | None = None,
    clone_depth: int | None = None,
    **overrides: Any,
) -> GeneratorSettings:
    cfg = config_path if config_path and pathlib.Path(config_path).is_file() else None
    if config_path and config_path != paths.CFG_DEFAULT and cfg is None:
        msg = f"Config file {config_path!r} does not exist."
        raise t.BadParameter(msg)
    return GeneratorSettings.load(
        config_file=cfg,
        build_fn=build_fn,
        repo_path=repo_path,
        clone_depth=clone_depth,
        **overrides,
    )


def _generate(settings: GeneratorSettings, engine: str) -> Writer:
    from mknodes.site import generate_output
    from mknodes.site.writers import get_writer

    writer = get_writer(engine)(settings)
    output = generate_output(settings, flavor=writer.resolved_flavor)
    cfg_path = writer.write(output)
    logger.info("Generated %s pages, config: %s", len(output.pages), cfg_path)
    return writer


def _generate_args(engine: str, **opts: Any) -> list[str]:
    names = {
        "config_path": "--config-path",
        "build_fn": "--build-fn",
        "repo_path": "--repo-url",
        "clone_depth": "--clone-depth",
        "generated_dir": "--generated-dir",
        "flavor": "--flavor",
    }
    args = ["--engine", engine]
    for key, value in opts.items():
        if value is not None:
            args += [names[key], str(value)]
    return args
