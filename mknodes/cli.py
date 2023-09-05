from __future__ import annotations

import io
import os
import pathlib
import sys

import click

from mkdocs.commands.build import build
from mkdocs.commands.serve import serve
from mkdocs.config import load_config

from mknodes.utils import yamlhelpers


CONTENT = """
import mknodes

def build(project):
    root = project.get_root()
    page = root.add_index_page(hide_toc=True)
    page += '''{node}'''


"""


@click.group()
def cli():
    """Main entrypoint."""


@cli.command()
@click.option("-r", "--repo-url", help="Repo url of package to create a website for.")
@click.option("-s", "--site-script", help="Path to script used for building website.")
@click.option("-d", "--site-dir", help="Directory to create the website in.")
def create(repo_url, site_script, site_dir="site"):
    """Create website."""
    print(f"{repo_url=} {site_script=} {site_dir=}")
    cfg = yamlhelpers.load_yaml_file("mkdocs_generic.yml")
    for plugin in cfg["plugins"]:
        if "mknodes" in plugin:
            plugin["mknodes"]["repo_path"] = repo_url
            plugin["mknodes"]["path"] = site_script
    cfg["site_dir"] = site_dir
    text = yamlhelpers.dump_yaml(cfg)
    buffer = io.StringIO(text)
    config = load_config(buffer)
    config["plugins"].run_event("startup", command="build", dirty=False)
    build(config)
    config["plugins"].run_event("shutdown")


@cli.command()
@click.option("-r", "--repo-url", help="Repo url of package to create a website for.")
@click.option("-s", "--site-script", help="Path to script used for building website.")
def serve_page(repo_url, site_script, site_dir="site"):
    """Create website."""
    print(f"{repo_url=} {site_script=} {site_dir=}")
    cfg = yamlhelpers.load_yaml_file("mkdocs_generic.yml")
    for plugin in cfg["plugins"]:
        if "mknodes" in plugin:
            plugin["mknodes"]["repo_path"] = repo_url
            plugin["mknodes"]["path"] = site_script
    text = yamlhelpers.dump_yaml(cfg)
    print(text)
    buffer = io.StringIO(text)
    # config = load_config(buffer)
    # config["plugins"].run_event("startup", command="build", dirty=False)
    serve(buffer)
    # config["plugins"].run_event("shutdown")


def serve_script(script_file: str | os.PathLike):
    abs_script_file = pathlib.Path(script_file).absolute()
    script_file = abs_script_file.relative_to(pathlib.Path.cwd())
    # path = ".".join(abs_script_file.parts).removeprefix(".py")
    text = pathlib.Path("mkdocs.yml").read_text()
    config_file = yamlhelpers.load_yaml(text)
    for plugin in config_file["plugins"]:
        if isinstance(plugin, dict) and next(iter(plugin.keys())) == "mknodes":
            plugin["mknodes"]["path"] = str(abs_script_file)  # path
    output = yamlhelpers.dump_yaml(config_file)
    stream = io.StringIO(output)
    serve.serve(
        config_file=stream,  # type: ignore
        dev_addr=None,
        livereload=True,  # type: ignore
        build_type=None,
        watch_theme=False,
        watch=[],
    )


def serve_node(node):
    text = CONTENT.format(node=str(node))

    p = pathlib.Path("docs/test.py")
    p.write_text(text)
    # file = tempfile.NamedTemporaryFile("w")
    # file.write(text)
    serve_script(p)


if __name__ == "__main__":
    # cli(["build", "--help"])
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
