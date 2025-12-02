"""Exporters for writing build output to disk."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Protocol

import upath
import yamling


if TYPE_CHECKING:
    from pathlib import Path

    from mknodes.build.output import BuildOutput


class Exporter(Protocol):
    """Protocol for exporters."""

    async def export(self, output: BuildOutput, target: Path) -> None:
        """Export build output to target directory."""
        ...


class MarkdownExporter:
    """Writes markdown files with per-file metadata sidecars."""

    def __init__(self, metadata_suffix: str = ".meta.yaml"):
        """Constructor.

        Args:
            metadata_suffix: Suffix for metadata sidecar files.
        """
        self.metadata_suffix = metadata_suffix

    async def export(self, output: BuildOutput, target: Path) -> None:
        """Export build output to target directory.

        Args:
            output: Build output to export.
            target: Target directory for output files.
        """
        target_path = upath.UPath(target)
        target_path.mkdir(parents=True, exist_ok=True)

        for file_path, content in output.files.items():
            full_path = target_path / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)

            # Write content
            if isinstance(content, bytes):
                full_path.write_bytes(content)
            else:
                full_path.write_text(content, encoding="utf-8")
            # Write metadata sidecar
            metadata = {"generated_by": "mknodes", "path": file_path}
            meta_path = full_path.with_suffix(full_path.suffix + self.metadata_suffix)
            meta_path.write_text(yamling.dump_yaml(metadata, indent=2), encoding="utf-8")

        # Write combined metadata file
        meta: dict[str, Any] = {}
        if output.resources:
            meta["resources"] = {
                "markdown_extensions": output.resources.markdown_extensions,
                "css": output.resources.css,
                "js": output.resources.js,
                "plugins": output.resources.plugins,
                "packages": output.resources.packages,
            }
        if output.nav_structure:
            meta["nav"] = output.nav_structure
        if meta:
            meta_path = target_path / ".mknodes.meta.yaml"
            meta_path.write_text(yamling.dump_yaml(meta, indent=2), encoding="utf-8")
