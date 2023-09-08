from __future__ import annotations

import logging
import sys

import click

from mknodes.cli import cli_options

from mknodes.plugin import mkdocshelpers
from mknodes.utils import yamlhelpers


logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

logger = logging.getLogger(__name__)


@click.group()
def cli():
    """MkNodes CLI interface."""


@cli.command()
@cli_options.repo_url_option
@cli_options.site_script_option
@cli_options.site_dir_option
@cli_options.clone_depth_option
@cli_options.common_options  # config-file / strict / theme / use-directory-urls
@cli_options.debug_options  # verbose / quiet
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
        config_file,
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
@cli_options.common_options  # config-file / strict / theme / use-directory-urls
@cli_options.debug_options  # verbose / quiet
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
@cli_options.debug_options  # verbose / quiet
def create_config(repo_url, site_script: str, theme: str | None, **kwargs):
    """Serve a MkNodes-based website."""
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
    from mknodes.info import folderinfo
    from mknodes.utils import helpers

    if helpers.is_url(repo_url):
        repo = folderinfo.FolderInfo.clone_from(repo_url, depth=1)
    else:
        repo = repo_url

    skin = theme_.Theme(theme_name)
    proj = project.Project(
        base_url="",
        use_directory_urls=True,
        theme=skin,
        repo=repo,
        build_fn=site_script,
    )
    info = proj.infocollector
    config["markdown_extensions"] = info["markdown_extensions"]
    if social := info["metadata"]["social_info"]:
        config["extra"]["social"] = social  # type: ignore[index]
    config["repo_url"] = info["metadata"]["repository_url"]
    config["site_description"] = info["metadata"]["summary"]
    config["site_name"] = info["metadata"]["name"]
    config["site_author"] = info["project"].info.author_name
    result = yamlhelpers.dump_yaml(config)
    print(result)


if __name__ == "__main__":
    cli(sys.argv)
