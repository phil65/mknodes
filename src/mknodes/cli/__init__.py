"""MkNodes CLI: `build` / `serve` / `generate` (site generator), `render` / `render-folder`."""

from __future__ import annotations

import logfire

from mknodes.cli import render, site
from mknodes.cli.app import cli


def main() -> None:
    """Entry point for the `mknodes` CLI."""
    logfire.configure(console=False, send_to_logfire="if-token-present", service_name="mknodes")
    cli()


__all__ = ["cli", "main", "render", "site"]
