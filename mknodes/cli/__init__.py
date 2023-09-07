from __future__ import annotations

import logging
import sys

import click

from mknodes.cli import cli_options

from mknodes.plugin import mkdocshelpers


logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)


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


# @cli.command()
# @cli_options.repo_url_option
# @cli_options.site_script_option
# @cli_options.config_path_option
# @cli_options.theme_option
# @cli_options.directory_urls_option
# @cli_options.debug_options # verbose / quiet
# def create_config(config_path, repo_url, site_script: str, **kwargs):
#     """Serve a MkNodes-based website."""
#     mknodes_plugin = dict(
#         mknodes={"repo_path": repo_url, "path": site_script, "clone_depth": 1},
#     )
#     cfg = {
#         "site_name": "Not set",
#         "plugins": [
#             "search",
#             "section-index",
#             "mkdocstrings",
#             "literate-nav",
#             mknodes_plugin,
#         ],
#     }
#     text = yamlhelpers.dump_yaml(cfg)
#     buffer = io.StringIO(text)
#     config = load_config(buffer, **kwargs)
#     build_.build(config)


if __name__ == "__main__":
    cli(sys.argv)
