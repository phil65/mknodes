from __future__ import annotations

from mknodes.utils import log
import sys

import rich_click as click

from mknodes.cli import cli_options

from mknodes.plugin import mkdocshelpers
from mknodes.utils import yamlhelpers


logger = log.get_logger(__name__)

click.rich_click.USE_RICH_MARKUP = True


@click.group()
def cli():
    """MkNodes CLI interface."""


@cli.command()
@cli_options.repo_url_option
@cli_options.site_script_option
@cli_options.site_dir_option
@cli_options.clone_depth_option
@cli_options.config_path_option
@cli_options.strict_option
@cli_options.theme_option
@cli_options.use_directory_urls_option
@cli_options.verbose_option
@cli_options.quiet_option
def build(
    repo_url,
    site_script: str,
    clone_depth: int = 1,
    site_dir="site",
    config_file=None,
    **kwargs,
):
    """Create a MkNodes-based website."""
    cfg = mkdocshelpers.load_and_patch_config(
        config_file or "mkdocs_basic.yml",
        repo_url=repo_url,
        site_script=site_script,
        clone_depth=clone_depth,
    )
    cfg["site_dir"] = site_dir
    mkdocshelpers.build(cfg, **kwargs)


@cli.command()
@cli_options.repo_url_option
@cli_options.site_script_option
@cli_options.clone_depth_option
@cli_options.config_path_option
@cli_options.strict_option
@cli_options.theme_option
@cli_options.use_directory_urls_option
@cli_options.verbose_option
@cli_options.quiet_option
def serve(repo_url, site_script: str, clone_depth: int = 1, config_file=None, **kwargs):
    """Serve a MkNodes-based website."""
    cfg = mkdocshelpers.load_and_patch_config(
        config_file,
        repo_url=repo_url,
        site_script=site_script,
        clone_depth=clone_depth,
    )
    mkdocshelpers.serve(cfg, **kwargs)


@cli.command()
@cli_options.repo_url_option
@cli_options.site_script_option
@cli_options.config_path_option
@cli_options.theme_option
@cli_options.use_directory_urls_option
@cli_options.verbose_option
@cli_options.quiet_option
def create_config(repo_url: str, site_script: str, theme: str | None, **kwargs):
    """Create a config based on given script and repository."""
    mknodes_plugin = dict(
        mknodes={"repo_path": repo_url, "path": site_script},
    )
    theme_name = theme or "material"
    config = {
        "site_name": "Not set",
        "theme": theme_name,
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
        repo=repo_url,
        build_fn=site_script,
        clone_depth=1,
    )
    requirements = proj.get_requirements()
    info = proj.context.info
    config["markdown_extensions"] = requirements.markdown_extensions
    if social := info.social_info:
        config["extra"]["social"] = social  # type: ignore[index]
    config["repo_url"] = info.repository_url
    config["site_description"] = info.summary
    config["site_name"] = info.distribution_name
    config["site_author"] = info.author_name
    result = yamlhelpers.dump_yaml(config)
    print(result)


if __name__ == "__main__":
    cli(sys.argv)
