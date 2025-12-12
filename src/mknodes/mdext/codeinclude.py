"""Code Include Extension.

A preprocessor extension that includes external files wrapped in fenced code blocks
with automatic syntax highlighting and title based on filename.

Example:
    ```markdown
    @@@codeinclude "path/to/file.py"
    ```

    Becomes:
    ```python title="file.py"
    <file content>
    ```
"""

from __future__ import annotations

import os
from pathlib import Path
import re
from typing import TYPE_CHECKING

from markdown import Extension
from markdown.preprocessors import Preprocessor
from markdown.util import ETX, STX
from upath import UPath


if TYPE_CHECKING:
    from markdown import Markdown


# Language mapping from file extensions
EXTENSION_TO_LANGUAGE = {
    ".py": "python",
    ".js": "javascript",
    ".ts": "typescript",
    ".jsx": "jsx",
    ".tsx": "tsx",
    ".java": "java",
    ".c": "c",
    ".cpp": "cpp",
    ".cc": "cpp",
    ".cxx": "cpp",
    ".h": "c",
    ".hpp": "cpp",
    ".cs": "csharp",
    ".go": "go",
    ".rs": "rust",
    ".rb": "ruby",
    ".php": "php",
    ".swift": "swift",
    ".kt": "kotlin",
    ".scala": "scala",
    ".sh": "bash",
    ".bash": "bash",
    ".zsh": "zsh",
    ".fish": "fish",
    ".ps1": "powershell",
    ".r": "r",
    ".R": "r",
    ".sql": "sql",
    ".html": "html",
    ".htm": "html",
    ".xml": "xml",
    ".css": "css",
    ".scss": "scss",
    ".sass": "sass",
    ".less": "less",
    ".json": "json",
    ".yaml": "yaml",
    ".yml": "yaml",
    ".toml": "toml",
    ".ini": "ini",
    ".cfg": "ini",
    ".conf": "conf",
    ".md": "markdown",
    ".rst": "rst",
    ".tex": "latex",
    ".vim": "vim",
    ".lua": "lua",
    ".pl": "perl",
    ".asm": "asm",
    ".s": "asm",
    ".dockerfile": "dockerfile",
    ".gitignore": "gitignore",
    ".env": "bash",
    ".txt": "text",
}


class CodeIncludeError(Exception):
    """Code include error."""


class CodeIncludePreprocessor(Preprocessor):
    """Handle code includes in Markdown content."""

    RE_INCLUDE = re.compile(
        r'^(?P<space>[ \t]*)@@@codeinclude[ \t]+"(?P<path>(?:\\"|[^"\n\r])+?)"[ \t]*$',
        re.MULTILINE,
    )

    def __init__(self, config: dict, md: Markdown):
        """Initialize preprocessor."""
        base = config.get("base_path")
        if isinstance(base, (str, os.PathLike)):
            base = [base]
        self.base_path = [Path(b).resolve() for b in base] if base is not None else []
        self.check_paths = config.get("check_paths")
        self.placeholder_cache: dict[str, str] = {}
        self.placeholder_counter = 0
        super().__init__()

    def get_language_from_path(self, path: str) -> str:
        """Determine language from file extension."""
        suffix = Path(path).suffix.lower()
        return EXTENSION_TO_LANGUAGE.get(suffix, "text")

    def get_snippet_path(self, path: str) -> UPath | None:
        """Get snippet path from base paths."""
        # Try as absolute or URL first
        upath = UPath(path)
        if upath.exists():
            return upath

        # Try relative to base paths
        for base in self.base_path:
            candidate = base / path
            upath = UPath(candidate)
            if upath.exists():
                return upath

        return None

    def process_include(self, path: str) -> str:
        """Process a single file include and wrap in code block."""
        snippet_path = self.get_snippet_path(path)
        if not snippet_path:
            if self.check_paths:
                msg = f"File at path '{path}' could not be found"
                raise CodeIncludeError(msg)
            return ""

        try:
            content = snippet_path.read_text()
        except Exception as e:
            if self.check_paths:
                msg = f"Error reading '{path}': {e}"
                raise CodeIncludeError(msg) from e
            return ""

        # Get language and filename
        filename = Path(path).name
        language = self.get_language_from_path(path)

        # Build code block with proper fenced code syntax
        # Use placeholder to protect from premature markdown processing
        code_block = f'```{language} title="{filename}"\n{content.rstrip()}\n```'

        # Create unique placeholder with counter to avoid collisions
        self.placeholder_counter += 1
        placeholder = f"{STX}codeinclude-{self.placeholder_counter}{ETX}"

        # Store for later replacement
        self.placeholder_cache[placeholder] = code_block

        return f"\n{placeholder}\n"

    def run(self, lines: list[str]) -> list[str]:
        """Process all includes in content."""
        content = "\n".join(lines)

        def replace_include(match: re.Match) -> str:
            path = match.group("path").strip()
            try:
                return self.process_include(path)
            except CodeIncludeError as e:
                if self.check_paths:
                    raise
                return f"<!-- Error including {path}: {e} -->"

        content = self.RE_INCLUDE.sub(replace_include, content)

        # Replace placeholders back with actual code blocks
        for placeholder, code_block in self.placeholder_cache.items():
            content = content.replace(placeholder, code_block)

        self.placeholder_cache.clear()
        self.placeholder_counter = 0

        return content.split("\n")


class CodeIncludeExtension(Extension):
    """Code Include extension."""

    def __init__(self, *args, **kwargs):
        """Initialize extension."""
        self.config = {
            "base_path": [["."], 'Base path for file paths - Default: ["."]'],
            "check_paths": [
                False,
                "Fail build if file not found - Default: False",
            ],
        }

        super().__init__(*args, **kwargs)

    def extendMarkdown(self, md: Markdown) -> None:  # noqa: N802
        """Register extension."""
        self.md = md
        md.registerExtension(self)
        config = self.getConfigs()
        processor = CodeIncludePreprocessor(config, md)
        md.preprocessors.register(processor, "codeinclude", 32)


def makeExtension(*args, **kwargs):  # noqa: N802
    """Return extension instance."""
    return CodeIncludeExtension(*args, **kwargs)
