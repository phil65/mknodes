from __future__ import annotations

import logging
import typer as t
from mkdocs import __main__ as mkdocs

from mknodes.info import mkdocsconfigfile
from mknodes.plugin import mkdocshelpers
from mknodes.utils import log, yamlhelpers


logger = log.get_logger(__name__)

cli = t.Typer(
    name="MkNodes",
    help="MkNodes CLI interface. Build websites from command line!",
    no_args_is_help=True,
)

REPO_HELP = "Repository URL of the target package."
BUILD_HELP = "Path to the build script."
SITE_DIR_HELP = "Path to the build script."
DEPTH_HELP = "Git clone depth in case repository is remote."
CFG_PATH_HELP = "Path to the config file"
STRICT_HELP = "Strict mode (fails on warnings)"
THEME_HELP = "Theme to use for the build."
USE_DIR_URLS_HELP = "Use directory URLs."
VERBOSE_HELP = "Enable verbose output."
QUIET_HELP = "Suppress output during build."


REPO_CMDS = "-r", "--repo-url"
SITE_DIR_CMDS = "-d", "--site-dir"
BUILD_CMS = "-b", "--build-fn"
DEPTH_CMDS = "-c", "--clone-depth"
CFG_PATH_CMDS = "-p", "--config-path"
STRICT_CMDS = "-s", "--strict"
THEME_CMDS = "-t", "--theme"
USE_DIR_URLS_CMDS = "-u", "--use-dir-urls"
VERBOSE_CMDS = "-v", "--verbose"
QUIET_CMDS = "-q", "--quiet"


def verbose(ctx, param, value):
    state = ctx.ensure_object(mkdocs.State)
    if value:
        state.stream.setLevel(logging.DEBUG)


def quiet(ctx, param, value):
    state = ctx.ensure_object(mkdocs.State)
    if value:
        state.stream.setLevel(logging.ERROR)


class State:
    """Maintain logging level."""

    def __init__(self, log_name="mkdocs", level=logging.INFO):
        from rich.logging import RichHandler

        self.logger = logging.getLogger(log_name)
        # Don't restrict level on logger; use handler
        self.logger.setLevel(1)
        self.logger.propagate = False
        self.stream = RichHandler(level, markup=False, rich_tracebacks=True)
        self.stream.name = "MkNodesStreamHandler"
        self.logger.addHandler(self.stream)

    def __del__(self):
        self.logger.removeHandler(self.stream)


@cli.command()
def build(
    repo_path: str = t.Option(None, *REPO_CMDS, help=REPO_HELP, show_default=False),
    build_fn: str = t.Option(None, *BUILD_CMS, help=BUILD_HELP, show_default=False),
    site_dir: str = t.Option("site", *SITE_DIR_CMDS, help=SITE_DIR_HELP),
    clone_depth: int = t.Option(None, *DEPTH_CMDS, help=DEPTH_HELP, show_default=False),
    config_path: str = t.Option("mkdocs_basic.yml", *CFG_PATH_CMDS, help=CFG_PATH_HELP),
    theme: str = t.Option("material", *THEME_CMDS, help=THEME_HELP),
    strict: bool = t.Option(False, *STRICT_CMDS, help=STRICT_HELP),
    use_directory_urls: bool = t.Option(True, *USE_DIR_URLS_CMDS, help=USE_DIR_URLS_HELP),
    _verbose: bool = t.Option(False, *VERBOSE_CMDS, help=VERBOSE_HELP, callback=verbose),
    _quiet: bool = t.Option(False, *QUIET_CMDS, help=QUIET_HELP, callback=quiet),
):
    """Create a MkNodes-based website."""
    cfg = mkdocsconfigfile.MkDocsConfigFile(config_path)
    cfg.update_mknodes_section(
        repo_url=repo_path,
        build_fn=build_fn,
        clone_depth=clone_depth,
    )
    cfg["site_dir"] = site_dir
    mkdocshelpers.build(
        cfg,
        strict=strict,
        theme=theme if theme != "material" else None,
        use_directory_urls=use_directory_urls,
    )


@cli.command()
def serve(
    repo_path: str = t.Option(None, *REPO_CMDS, help=REPO_HELP, show_default=False),
    build_fn: str = t.Option(None, *BUILD_CMS, help=BUILD_HELP, show_default=False),
    clone_depth: int = t.Option(None, *DEPTH_CMDS, help=DEPTH_HELP, show_default=False),
    config_path: str = t.Option("mkdocs_basic.yml", *CFG_PATH_CMDS, help=CFG_PATH_HELP),
    strict: bool = t.Option(False, *STRICT_CMDS, help=STRICT_HELP),
    theme: str = t.Option("material", *THEME_CMDS, help=THEME_HELP),
    use_directory_urls: bool = t.Option(True, *USE_DIR_URLS_CMDS, help=USE_DIR_URLS_HELP),
    _verbose: bool = t.Option(False, *VERBOSE_CMDS, help=VERBOSE_HELP, callback=verbose),
    _quiet: bool = t.Option(False, *QUIET_CMDS, help=QUIET_HELP, callback=quiet),
):
    """Serve a MkNodes-based website."""
    cfg = mkdocsconfigfile.MkDocsConfigFile(config_path)
    cfg.update_mknodes_section(
        repo_url=repo_path,
        build_fn=build_fn,
        clone_depth=clone_depth,
    )
    mkdocshelpers.serve(
        cfg,
        strict=strict,
        theme=theme if theme != "material" else None,
        use_directory_urls=use_directory_urls,
    )


@cli.command()
def create_config(
    repo_path: str = t.Option(None, *REPO_CMDS, help=REPO_HELP, show_default=False),
    build_fn: str = t.Option(None, *BUILD_CMS, help=BUILD_HELP, show_default=False),
    # config_path: str = t.Option("mkdocs_basic.yml", *CFG_PATH_CMDS, help=CFG_PATH_HELP),
    theme: str = t.Option("material", *THEME_CMDS, help=THEME_HELP),
    use_directory_urls: bool = t.Option(True, *USE_DIR_URLS_CMDS, help=USE_DIR_URLS_HELP),
    _verbose: bool = t.Option(False, *VERBOSE_CMDS, help=VERBOSE_HELP, callback=verbose),
    _quiet: bool = t.Option(False, *QUIET_CMDS, help=QUIET_HELP, callback=quiet),
):
    """Create a config based on given script and repository."""
    mknodes_plugin = dict(
        mknodes={"repo_path": repo_path, "path": build_fn},
    )
    theme_name = theme or "material"
    config = {
        "site_name": "Not set",
        "theme": theme_name,
        "use_directory_urls": use_directory_urls,
        "extra": {},
        "plugins": [
            "search",
            "section-index",
            "mkdocstrings",
            "literate-nav",
            mknodes_plugin,
        ],
    }

    from mknodes import project
    from mknodes.theme import theme as theme_

    skin = theme_.Theme(theme_name)
    proj = project.Project(
        base_url="",
        use_directory_urls=True,
        theme=skin,
        repo=repo_path,
        build_fn=build_fn,
        clone_depth=1,
    )
    requirements = proj.get_requirements()
    info = proj.context.metadata
    config["markdown_extensions"] = requirements.markdown_extensions
    if social := info.social_info:
        config["extra"]["social"] = social  # type: ignore[index]
    config["repo_path"] = info.repository_url
    config["site_description"] = info.summary
    config["site_name"] = info.distribution_name
    config["site_author"] = info.author_name
    result = yamlhelpers.dump_yaml(config)
    print(result)


if __name__ == "__main__":
    cli(["build", "--help"])
