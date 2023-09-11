"""The Mkdocs Plugin."""

from __future__ import annotations

from collections.abc import Mapping
import io
import os
import pathlib

from typing import Any

from mkdocs.commands import build as build_, serve as serve_
from mkdocs.config import load_config
from mkdocs.config.defaults import MkDocsConfig
from mkdocs.plugins import get_plugin_logger
from mkdocs.structure.files import File, Files

from mknodes.utils import yamlhelpers


logger = get_plugin_logger(__name__)


def file_sorter(f: File):
    parts = pathlib.PurePath(f.src_path).parts
    return tuple(
        chr(f.name != "index" if i == len(parts) - 1 else 2) + p
        for i, p in enumerate(parts)
    )


def merge_files(*files: Files) -> Files:
    file_list = [i for j in files for i in j]
    return Files(sorted(file_list, key=file_sorter))


def build(config: MkDocsConfig | Mapping[str, Any], **kwargs):
    match config:
        case Mapping():
            text = yamlhelpers.dump_yaml(config)
            buffer = io.StringIO(text)
            config = load_config(buffer, **kwargs)
    for k, v in config.items():
        logger.debug("%s: %s", k, v)
    config.plugins.run_event("startup", command="build", dirty=False)
    build_.build(config)
    config.plugins.run_event("shutdown")


def serve(
    config: str | os.PathLike | MkDocsConfig | Mapping[str, Any] = "mkdocs_basic.yml",
    **kwargs,
):
    """Serve a MkNodes-based website."""
    match config:
        case str() | os.PathLike():
            cfg = yamlhelpers.load_yaml_file(config)
        case dict():
            cfg = config
        case MkDocsConfig():
            cfg = dict(config)
    text = yamlhelpers.dump_yaml(cfg)
    for k, v in cfg.items():
        logger.debug("%s: %s", k, v)
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


def load_and_patch_config(
    config: str | os.PathLike | dict,
    repo_url: str = ".",
    site_script: str = "",
    clone_depth: int = 1,
):
    if isinstance(config, str | os.PathLike | None):
        cfg = yamlhelpers.load_yaml_file(config or "mkdocs_basic.yml")
    else:
        cfg = config
    for plugin in cfg["plugins"]:
        if "mknodes" in plugin:
            plugin["mknodes"]["repo_path"] = repo_url
            plugin["mknodes"]["path"] = site_script
            plugin["mknodes"]["clone_depth"] = clone_depth
    return cfg
