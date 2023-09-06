"""The Mkdocs Plugin."""

from __future__ import annotations

from mkdocs.config import base, config_options as c


class PluginConfig(base.Config):
    path = c.Type(str)
    """Path to the build script."""
    repo_path = c.Type(str, default=".")
    """Path to the repository to document."""
    clone_depth = c.Type(int, default=100)
    """Clone depth in case the repository is remote. (Required for git-changelog)."""
    build_folder = c.Optional(c.Type(str))
    """Folder to create the Markdown files in. (Default: Temporary dir)"""
