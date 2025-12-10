"""Helper for parsing optional dependencies from pyproject.toml with comment descriptions."""

from __future__ import annotations

from dataclasses import dataclass
import re
import tomllib
from typing import Literal


@dataclass
class DependencyGroup:
    """An optional dependency group with its metadata."""

    name: str
    dependencies: list[str]
    description: str | None


def parse_dependencies(
    toml_content: str,
    source: Literal["extras", "groups"] = "extras",
) -> list[DependencyGroup]:
    """Parse optional dependencies from pyproject.toml content.

    Extracts descriptions from inline comments on the closing bracket line.

    Args:
        toml_content: Raw pyproject.toml content as string.
        source: Where to read dependencies from:
            - "extras": `[project.optional-dependencies]`
            - "groups": `[dependency-groups]`

    Returns:
        List of DependencyGroup objects with name, dependencies, and description.

    Example:
        ```
        toml = '''
        [project.optional-dependencies]
        clipboard = ["clipman"]  # Clipboard functionality
        coding = [
            "ast-grep-py>=0.40.0",
        ]  # Packages for coding
        '''
        deps = parse_dependencies(toml)
        # deps[0].name == "clipboard"
        # deps[0].description == "Clipboard functionality"
        ```
    """
    # Parse TOML to get structured data
    data = tomllib.loads(toml_content)

    match source:
        case "extras":
            optional_deps = data.get("project", {}).get("optional-dependencies", {})
        case "groups":
            optional_deps = data.get("dependency-groups", {})

    if not optional_deps:
        return []

    # Extract comments from raw content
    comments = _extract_comments(toml_content, set(optional_deps.keys()))

    return [
        DependencyGroup(
            name=name,
            dependencies=list(deps),
            description=comments.get(name),
        )
        for name, deps in optional_deps.items()
    ]


def _extract_comments(toml_content: str, dep_names: set[str]) -> dict[str, str]:
    """Extract inline comments for each dependency group.

    Handles both single-line and multi-line array definitions.
    """
    comments: dict[str, str] = {}
    lines = toml_content.splitlines()
    # Pattern for single-line: `name = [...]  # comment`
    single_line_pattern = re.compile(r"^([\w-]+)\s*=\s*\[.*?\]\s*#\s*(.+)$")
    # Pattern for multi-line closing: `]  # comment`
    closing_pattern = re.compile(r"^\s*\]\s*#\s*(.+)$")
    # Pattern for multi-line opening: `name = [`
    opening_pattern = re.compile(r"^([\w-]+)\s*=\s*\[\s*$")
    current_dep: str | None = None
    for line in lines:
        # Check single-line definition
        if match := single_line_pattern.match(line):
            name, comment = match.groups()
            if name in dep_names:
                comments[name] = comment.strip()
            continue

        # Check multi-line opening
        if match := opening_pattern.match(line):
            name = match.group(1)
            if name in dep_names:
                current_dep = name
            continue

        # Check multi-line closing with comment
        if current_dep and (match := closing_pattern.match(line)):
            comments[current_dep] = match.group(1).strip()
            current_dep = None
            continue

        # Check plain closing bracket (reset state)
        if current_dep and line.strip().startswith("]"):
            current_dep = None

    return comments
