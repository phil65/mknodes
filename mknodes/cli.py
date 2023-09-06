from __future__ import annotations

import io
import logging
import pathlib
import sys

import click

from mkdocs import __main__ as mkdocs
from mkdocs.commands import build as build_, serve as serve_
from mkdocs.config import load_config

from mknodes.utils import yamlhelpers


logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)


def callback(ctx, param, value):
    state = ctx.ensure_object(mkdocs.State)
    if value:
        state.stream.setLevel(logging.DEBUG)


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
    **kwargs,
):
    """Create a MkNodes-based website."""
    print(f"{repo_url=} {site_script=} {site_dir=}")
    cfg = yamlhelpers.load_yaml_file("mkdocs_generic.yml")
    for plugin in cfg["plugins"]:
        if "mknodes" in plugin:
            plugin["mknodes"]["repo_path"] = repo_url
            plugin["mknodes"]["path"] = site_script
            plugin["mknodes"]["clone_depth"] = clone_depth
    cfg["site_dir"] = site_dir
    text = yamlhelpers.dump_yaml(cfg)
    buffer = io.StringIO(text)
    config = load_config(buffer, **kwargs)
    # config["plugins"].run_event("startup", command="build", dirty=False)
    build_.build(config)
    # config["plugins"].run_event("shutdown")


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
    cfg = yamlhelpers.load_yaml_file(config_file or "mkdocs.yml")
    for plugin in cfg["plugins"]:
        if "mknodes" in plugin:
            plugin["mknodes"]["repo_path"] = repo_url
            plugin["mknodes"]["path"] = site_script
            plugin["mknodes"]["clone_depth"] = clone_depth
    text = yamlhelpers.dump_yaml(cfg)
    stream = io.StringIO(text)
    serve_.serve(config_file=stream, livereload=False, **kwargs)  # type: ignore[arg-type]


def serve_node(node, repo_path: str = "."):
    text = f"""
    import mknodes

    def build(project):
        root = project.get_root()
        page = root.add_index_page(hide_toc=True)
        page += '''{node!s}'''


    """
    p = pathlib.Path("docs/test.py")
    p.write_text(text)
    serve(repo_url=repo_path, site_script=p)


if __name__ == "__main__":
    cli(sys.argv)
    # cli(
    #     [
    #         "create",
    #         "-r",
    #         "https://github.com/mkdocs/mkdocs.git",
    #         "-s",
    #         "mknodes.mkwebsite:MkWebSite.for_project",
    #         "-d",
    #         "site/test",
    #     ],
    # )
