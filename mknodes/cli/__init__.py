from __future__ import annotations

import logging
from mknodes.utils import log
import typer as t
from mkdocs import __main__ as mkdocs


from mknodes.plugin import mkdocshelpers
from mknodes.utils import yamlhelpers

logger = log.get_logger(__name__)

cli = t.Typer(
    name="MkNodes",
    help="MkNodes CLI interface. Build websites from command line!",
    no_args_is_help=True,
)

DEFAULT_FN = "mknodes.navs.mkwebsite:MkWebSite.for_project"
REPO_URL_HELP = "Repository URL of the target package."
BUILD_CMD_HELP = "Path to the build script."
SITE_DIR_HELP = "Path to the build script."
CLONE_DEPTH_HELP = "Git clone depth in case repository is remote."
CFG_PATH_HELP = "Path to the config file"
STRICT_HELP = "Strict mode (fails on warnings)"
THEME_HELP = "Theme to use for the build."
USE_DIR_URLS_HELP = "Use directory URLs."
VERBOSE_HELP = "Enable verbose output."
QUIET_HELP = "Suppress output during build."


REPO_URL_CMDS = "-r", "--repo-url"
SITE_DIR_CMDS = "-d", "--site-dir"
BUILD_FN_CMDS = "-b", "--build-fn"
CLONE_DEPTH_CMDS = "-c", "--clone-depth"
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


@cli.command()
def build(
    repo_path: str = t.Option(".", *REPO_URL_CMDS, help=REPO_URL_HELP),
    build_fn: str = t.Option(DEFAULT_FN, *BUILD_FN_CMDS, help=BUILD_CMD_HELP),
    site_dir: str = t.Option("site", *SITE_DIR_CMDS, help=SITE_DIR_HELP),
    clone_depth: int = t.Option(1, *CLONE_DEPTH_CMDS, help=CLONE_DEPTH_HELP),
    config_path: str = t.Option("mkdocs_basic.yml", *CFG_PATH_CMDS, help=CFG_PATH_HELP),
    theme: str = t.Option("material", *THEME_CMDS, help=THEME_HELP),
    strict: bool = t.Option(False, *STRICT_CMDS, help=STRICT_HELP),
    use_directory_urls: bool = t.Option(True, *USE_DIR_URLS_CMDS, help=USE_DIR_URLS_HELP),
    verbose: bool = t.Option(False, *VERBOSE_CMDS, help=VERBOSE_HELP, callback=verbose),
    quiet: bool = t.Option(False, *QUIET_CMDS, help=QUIET_HELP, callback=quiet),
):
    """Create a MkNodes-based website."""
    cfg = mkdocshelpers.load_and_patch_config(
        config_path or "mkdocs_basic.yml",
        repo_url=repo_path,
        site_script=build_fn,
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
    repo_path: str = t.Option(".", *REPO_URL_CMDS, help=REPO_URL_HELP),
    build_fn: str = t.Option(DEFAULT_FN, *BUILD_FN_CMDS, help=BUILD_CMD_HELP),
    clone_depth: int = t.Option(1, *CLONE_DEPTH_CMDS, help=CLONE_DEPTH_HELP),
    config_path: str = t.Option("mkdocs_basic.yml", *CFG_PATH_CMDS, help=CFG_PATH_HELP),
    strict: bool = t.Option(False, *STRICT_CMDS, help=STRICT_HELP),
    theme: str = t.Option("material", *THEME_CMDS, help=THEME_HELP),
    use_directory_urls: bool = t.Option(True, *USE_DIR_URLS_CMDS, help=USE_DIR_URLS_HELP),
    verbose: bool = t.Option(False, *VERBOSE_CMDS, help=VERBOSE_HELP, callback=verbose),
    quiet: bool = t.Option(False, *QUIET_CMDS, help=QUIET_HELP, callback=quiet),
):
    """Serve a MkNodes-based website."""
    cfg = mkdocshelpers.load_and_patch_config(
        config_path,
        repo_url=repo_path,
        site_script=build_fn,
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
    repo_path: str = t.Option(".", *REPO_URL_CMDS, help=REPO_URL_HELP),
    build_fn: str = t.Option(DEFAULT_FN, *BUILD_FN_CMDS, help=BUILD_CMD_HELP),
    # config_path: str = t.Option("mkdocs_basic.yml", *CFG_PATH_CMDS, help=CFG_PATH_HELP),
    theme: str = t.Option("material", *THEME_CMDS, help=THEME_HELP),
    use_directory_urls: bool = t.Option(True, *USE_DIR_URLS_CMDS, help=USE_DIR_URLS_HELP),
    verbose: bool = t.Option(False, *VERBOSE_CMDS, help=VERBOSE_HELP, callback=verbose),
    quiet: bool = t.Option(False, *QUIET_CMDS, help=QUIET_HELP, callback=quiet),
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
