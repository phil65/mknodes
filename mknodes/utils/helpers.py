from __future__ import annotations

from collections.abc import Callable, Generator, Iterable, Sequence
import functools
import itertools
import os
import re

from typing import TypeVar

from mknodes.utils import log


logger = log.get_logger(__name__)


@functools.cache
def get_svg_for_code(
    text: str,
    title: str = "",
    width: int = 80,
    language: str = "python",
    pygments_style: str = "material",
):
    from rich.console import Console
    from rich.padding import Padding
    from rich.syntax import Syntax

    with open(os.devnull, "w") as devnull:  # noqa: PTH123
        console = Console(record=True, width=width, file=devnull, markup=False)
        renderable = Syntax(text, lexer=language, theme=pygments_style)
        renderable = Padding(renderable, (0,), expand=False)
        console.print(renderable, markup=False)
    return console.export_svg(title=title)


def to_str_if_textnode(node):
    import mknodes

    return str(node) if type(node) in {mknodes.MkText, mknodes.MkHeader} else node


def escaped(text: str, entity_type: str | None = None) -> str:
    """Helper function to escape markup.

    Args:
        text: The text.
        entity_type: For the entity types ``PRE``, ``CODE`` and the link
                     part of ``TEXT_LINKS``, only certain characters need to be escaped.
    """
    if entity_type in ["pre", "code"]:
        escape_chars = r"\`"
    elif entity_type == "text_link":
        escape_chars = r"\)"
    else:
        escape_chars = r"_*[]()~`>#+-=|{}.!"

    return re.sub(f"([{re.escape(escape_chars)}])", r"\\\1", text)


def slugify(text: str | os.PathLike) -> str:
    """Create a slug for given text.

    Returned text only contains alphanumerical and underscore.

    Arguments:
        text: text to get a slug for
    """
    text = str(text).lower()
    text = re.sub("[^0-9a-zA-Z_.]", "_", text)
    return re.sub("^[^a-zA-Z_#]+", "", text)


def groupby(data, keyfunc: Callable | None = None) -> dict[str, list]:
    data = sorted(data, key=keyfunc or (lambda x: x))
    return {k: list(g) for k, g in itertools.groupby(data, keyfunc)}


def groupby_first_letter(data, keyfunc: Callable | None = None) -> dict[str, list]:
    data = sorted(data, key=keyfunc or (lambda x: x))

    def first_letter(x):
        return keyfunc(x)[0] if keyfunc else x[0]

    return {k: list(g) for k, g in itertools.groupby(data, first_letter)}


def styled(
    text: str,
    *,
    size: int | None = None,
    bold: bool = False,
    italic: bool = False,
    code: bool = False,
) -> str:
    """Apply styling to given markdown.

    Arguments:
        text: Text to style
        size: Optional text size
        bold: Whether styled text should be bold
        italic: Whether styled text should be italic
        code: Whether styled text should styled as (inline) code
    """
    if size:
        text = f"<font size='{size}'>{text}</font>"
    if bold:
        text = f"**{text}**"
    if italic:
        text = f"*{text}*"
    if code:
        text = f"`{text}`"
    return text


def label_for_class(klass: type) -> str:
    mod = klass.__module__
    parts = mod.split(".")
    if mod.startswith("prettyqt."):
        return f"{parts[1]}.{klass.__name__}"
    return f"{parts[-1]}.{klass.__name__}"


T = TypeVar("T")


def batched(iterable: Iterable[T], n: int) -> Generator[tuple[T, ...], None, None]:
    """Batch data into tuples of length n. The last batch may be shorter."""
    # batched('ABCDEFG', 3) --> ABC DEF G
    if n < 1:
        msg = "n must be at least one"
        raise ValueError(msg)
    it = iter(iterable)
    while batch := tuple(itertools.islice(it, n)):
        yield batch


def get_indented_lines(lines: Iterable[str], indent: int | str = 4) -> list[str]:
    """Return all lines until a line is not indented with given indent.

    Returned lines are unindented.

    Arguments:
        lines: Lines to check for indented lines
        indent: Indentation to check
    """
    indent_str = indent if isinstance(indent, str) else " " * indent
    if indented := list(itertools.takewhile(lambda x: x.startswith(indent_str), lines)):
        return [j[len(indent_str) :] for j in indented]
    return []


def is_url(path: str) -> bool:
    return path.startswith(("http:/", "https:/", "www."))


def relative_url(url_a: str, url_b: str) -> str:
    """Compute the relative path from URL A to URL B.

    Arguments:
        url_a: URL A.
        url_b: URL B.

    Returns:
        The relative URL to go from A to B.
    """
    parts_a = url_a.split("/")
    if "#" in url_b:
        url_b, anchor = url_b.split("#", 1)
    else:
        anchor = None
    parts_b = url_b.split("/")

    # remove common left parts
    while parts_a and parts_b and parts_a[0] == parts_b[0]:
        parts_a.pop(0)
        parts_b.pop(0)

    # go up as many times as remaining a parts' depth
    levels = len(parts_a) - 1
    parts_relative = [".."] * levels + parts_b
    relative = "/".join(parts_relative)
    return f"{relative}#{anchor}" if anchor else relative


def get_output_from_call(call: Sequence[str]):
    import subprocess

    try:
        return subprocess.check_output(call).decode()
    except subprocess.CalledProcessError:
        logger.warning("Executing %s failed", call)
        return None


def get_nested_json(dct, *sections: str, keep_path: bool = False):
    # sourcery skip: merge-duplicate-blocks
    """Try to get data[sections[0]][sections[1]]...

    If Key path does not exist, return None.

    Arguments:
        dct: Dict to dig into
        sections: Sections to dig into
        keep_path: Return result with original nesting
    """
    section = dct
    for i in sections:
        if isinstance(section, dict):
            if child := section.get(i):
                section = child
            else:
                return None
        else:
            for idx in section:
                if i in idx and isinstance(idx, dict):
                    section = idx[i]
                    break
                if isinstance(idx, str) and idx == i:
                    section = idx
                    break
            else:
                return None
    if not keep_path:
        return section
    result: dict[str, dict] = {}
    new = result
    for sect in sections:
        result[sect] = section if sect == sections[-1] else {}
        result = result[sect]
    return new


if __name__ == "__main__":
    strings = groupby_first_letter([str(i) for i in range(1000)])
    print(strings)
