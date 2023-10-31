from __future__ import annotations

import functools
import os
import pathlib

from mknodes.utils import log


logger = log.get_logger(__name__)


def _walk_directory(directory: os.PathLike | str, tree) -> None:
    """Recursively build a Tree with directory contents."""
    # Sort dirs first then by filename
    from rich.filesize import decimal
    from rich.markup import escape
    from rich.text import Text

    paths = sorted(
        pathlib.Path(directory).iterdir(),
        key=lambda path: (path.is_file(), path.name.lower()),
    )
    for path in paths:
        # Remove hidden files
        if path.name.startswith("."):
            continue
        if path.is_dir():
            style = "dim" if path.name.startswith("__") else ""
            branch = tree.add(
                "[bold magenta]:open_file_folder: [link"
                f" file://{path}]{escape(path.name)}",
                style=style,
                guide_style=style,
            )
            _walk_directory(path, branch)
        else:
            text_filename = Text(path.name, "green")
            text_filename.highlight_regex(r"\..*$", "bold red")
            text_filename.stylize(f"link file://{path}")
            file_size = path.stat().st_size
            text_filename.append(f" ({decimal(file_size)})", "blue")
            icon = "🐍 " if path.suffix == ".py" else "📄 "
            tree.add(Text(icon) + text_filename)


@functools.cache
def get_folder_tree_svg(
    directory: str | os.PathLike,
    width: int = 80,
    title: str = "",
) -> str:
    from rich.console import Console
    from rich.tree import Tree

    tree = Tree(
        f":open_file_folder: [link file://{directory}]{directory}",
        guide_style="bold bright_blue",
    )
    _walk_directory(directory, tree)
    console = Console(record=True, width=width, markup=True)
    with console.capture() as _capture:
        # renderable = Padding(tree, (0,), expand=False)
        console.print(tree, markup=True)
    text = console.export_svg(title=title)
    return f"<body>\n\n{text}\n\n</body>\n\n"


@functools.cache
def get_svg_for_code(
    text: str,
    title: str = "",
    width: int = 80,
    language: str = "py",
    pygments_style: str = "material",
) -> str:
    from rich.console import Console
    from rich.padding import Padding
    from rich.syntax import Syntax

    # with console.capture() as _capture:
    with open(os.devnull, "w") as devnull:  # noqa: PTH123
        console = Console(record=True, width=width, file=devnull, markup=False)
        renderable = Syntax(text, lexer=language, theme=pygments_style)
        renderable = Padding(renderable, (0,), expand=False)
        console.print(renderable, markup=False)
    return console.export_svg(title=title)


if __name__ == "__main__":
    import rich

    strings = get_folder_tree_svg(".")
    rich.inspect(strings)
