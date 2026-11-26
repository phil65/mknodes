"""Exporters writing a `BuildOutput` to disk."""

from typing import TYPE_CHECKING, Protocol
import warnings

import upath

from mknodes.build.output import nav_to_markdown


if TYPE_CHECKING:
    from os import PathLike

    from mknodes.build.output import BuildOutput


SUMMARY_FILE = "SUMMARY.md"


class Exporter(Protocol):
    """Protocol for exporters."""

    def export_sync(self, output: BuildOutput, target: str | PathLike[str]) -> None:
        """Export build output to target directory."""
        ...


class MarkdownExporter:
    """Writes the pages and assets plus the nav as `SUMMARY.md`.

    The result is readable in any Markdown viewer (and on GitHub, with the `github`
    flavour). `SUMMARY.md` uses the literate-nav format.
    """

    def __init__(self, summary_file: str | None = SUMMARY_FILE) -> None:
        """Constructor.

        Args:
            summary_file: Filename for the nav (None: don't write the nav).
        """
        self.summary_file = summary_file

    def get_files(self, output: BuildOutput) -> dict[str, str | bytes]:
        """Return all files to write: path relative to the target -> content."""
        files = output.files
        if self.summary_file and output.nav:
            title = output.metadata.site_name or "Summary"
            files[self.summary_file] = f"# {title}\n\n{nav_to_markdown(output.nav)}\n"
        return files

    async def export(self, output: BuildOutput, target: str | PathLike[str]) -> None:
        """Deprecated (removed in 5.0): use `export_sync()`."""
        msg = "MarkdownExporter.export() is deprecated, use export_sync(). Removed in mknodes 5.0."
        warnings.warn(msg, DeprecationWarning, stacklevel=2)
        self.export_sync(output, target)

    def export_sync(self, output: BuildOutput, target: str | PathLike[str]) -> None:
        """Write the files of given output into target folder (local path or fsspec URL)."""
        target_path = upath.UPath(target)
        target_path.mkdir(parents=True, exist_ok=True)
        for file_path, content in self.get_files(output).items():
            full_path = target_path / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            if isinstance(content, bytes):
                full_path.write_bytes(content)
            else:
                full_path.write_text(content, encoding="utf-8")
