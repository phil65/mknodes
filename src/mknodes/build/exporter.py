"""Exporters for writing build output to disk."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any, Protocol

import upath


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

    def __init__(self, metadata_suffix: str = ".meta.json"):
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
            metadata = self._build_file_metadata(file_path, output)
            if metadata:
                meta_path = full_path.with_suffix(full_path.suffix + self.metadata_suffix)
                meta_path.write_text(
                    json.dumps(metadata, indent=2, default=str),
                    encoding="utf-8",
                )

        # Write global resources file
        if output.resources:
            resources_path = target_path / ".mknodes.resources.json"
            resources_path.write_text(
                json.dumps(self._serialize_resources(output.resources), indent=2),
                encoding="utf-8",
            )

        # Write nav structure
        if output.nav_structure:
            nav_path = target_path / ".mknodes.nav.json"
            nav_path.write_text(
                json.dumps(output.nav_structure, indent=2),
                encoding="utf-8",
            )

    def _build_file_metadata(
        self,
        file_path: str,
        output: BuildOutput,
    ) -> dict[str, Any]:
        """Build metadata dict for a single file.

        Args:
            file_path: Path of the file.
            output: Full build output for context.

        Returns:
            Metadata dictionary for the file.
        """
        # For now, just mark that this file was generated
        return {"generated_by": "mknodes", "path": file_path}

    def _serialize_resources(self, resources) -> dict[str, Any]:
        """Serialize Resources object to JSON-compatible dict.

        Args:
            resources: Resources object to serialize.

        Returns:
            JSON-serializable dictionary.
        """
        return {
            "markdown_extensions": self._serialize_extensions(resources.markdown_extensions),
            "css": [self._serialize_css(c) for c in resources.css],
            "js": [self._serialize_js(j) for j in resources.js],
            "plugins": [p.plugin_name for p in resources.plugins],
            "packages": [p.package_name for p in resources.packages],
        }

    def _serialize_extensions(self, extensions: dict[str, Any]) -> dict[str, Any]:
        """Serialize markdown extensions, handling non-serializable values.

        Args:
            extensions: Extension configuration dict.

        Returns:
            JSON-serializable dictionary.
        """
        result = {}
        for ext_name, ext_config in extensions.items():
            if isinstance(ext_config, dict):
                serialized_config = {}
                for k, v in ext_config.items():
                    if callable(v):
                        # Store function reference as string
                        serialized_config[k] = f"{v.__module__}:{v.__name__}"
                    else:
                        try:
                            json.dumps(v)
                            serialized_config[k] = v
                        except (TypeError, ValueError):
                            serialized_config[k] = str(v)
                result[ext_name] = serialized_config
            else:
                result[ext_name] = ext_config
        return result

    def _serialize_css(self, css) -> dict[str, Any]:
        """Serialize CSS resource."""
        from mknodes.utils.resources import CSSFile

        if isinstance(css, CSSFile):
            return {"type": "link", "link": css.link}
        return {"type": "text", "filename": css.filename, "content": css.content}

    def _serialize_js(self, js) -> dict[str, Any]:
        """Serialize JS resource."""
        from mknodes.utils.resources import JSFile

        if isinstance(js, JSFile):
            return {
                "type": "link",
                "link": js.link,
                "async": js.async_,
                "defer": js.defer,
                "is_library": js.is_library,
            }
        return {
            "type": "text",
            "filename": js.filename,
            "content": js.content,
            "is_library": js.is_library,
        }
