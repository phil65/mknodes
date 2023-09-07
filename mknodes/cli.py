from __future__ import annotations

import logging
import sys

import click

from mkdocs import __main__ as mkdocs

from mknodes.plugin import mkdocshelpers


logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)


@click.group()
def cli():
    """MkNodes CLI interface."""


@cli.command()
@click.option("-r", "--repo-url", help="Repo url of package to create a website for.")
@click.option(
    "-s",
    "--site-script",
    help="Path to script used for building website.",
    default="mknodes.mkwebsite:MkWebSite.for_project",
)
@click.option("-d", "--site-dir", help="Directory to create the website in.")
@click.option(
    "-c",
    "--clone-depth",
    help="How many commits to fetch if repository is remote.",
    type=int,
    default=100,
)
@mkdocs.common_config_options
@mkdocs.common_options
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
@click.option("-r", "--repo-url", help="Repo url of package to create a website for.")
@click.option(
    "-s",
    "--site-script",
    help="Path to script used for building website.",
    default="mknodes.mkwebsite:MkWebSite.for_project",
)
@click.option(
    "-c",
    "--clone-depth",
    help="How many commits to fetch if repository is remote.",
    type=int,
    default=100,
)
@mkdocs.common_config_options
@mkdocs.common_options
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
# @click.option("-r", "--repo-url", help="Repo url of package to create a config for.")
# @click.option(
#     "-s",
#     "--site-script",
#     help="Path where config should get created.",
#     default="mknodes.yml",
# )
# @click.option(
#     "-p",
#     "--config-path",
#     help="Path where config file should get written to.",
#     default="mknodes.mkwebsite:MkWebSite.for_project",
# )
# @click.option(
#     "-t",
#     "--theme",
#     type=click.Choice(mkdocs.theme_choices),
#     help="Theme to use",
# )
# @click.option(
#     "--use-directory-urls/--no-directory-urls",
#     is_flag=True,
#     default=None,
#     help=mkdocs.use_directory_urls_help,
# )
# @mkdocs.common_options
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
