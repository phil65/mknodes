"""The Mkdocs Plugin."""

from __future__ import annotations

from mkdocs.config import base, config_options as c


class PluginConfig(base.Config):
    path = c.Type(str)
    repo_path = c.Type(str, default=".")
    clone_depth = c.Type(int, default=100)
    build_folder = c.Optional(c.Type(str))
