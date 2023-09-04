from __future__ import annotations

from collections.abc import Callable, Generator, Iterable
import itertools
import logging
import os
import pathlib
import re

from typing import TypeVar


logger = logging.getLogger(__name__)


def to_str_if_textnode(node):
    import mknodes

    return str(node) if type(node) in {mknodes.MkText, mknodes.MkHeader} else node


def find_file_in_folder_or_parent(
    filename: str | pathlib.Path,
    folder: os.PathLike | str = ".",
) -> pathlib.Path | None:
    """Search for a file with given name in folder and its parent folders.

    Arguments:
        filename: File to search
        folder: Folder to start searching from
    """
    path = pathlib.Path(folder).absolute()
    while not (path / filename).exists() and len(path.parts) > 1:
        path = path.parent
    return file if (file := (path / filename)).exists() else None


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


def get_material_icon_path(icon: str) -> pathlib.Path:
    import material

    path = pathlib.Path(material.__path__[0])
    return path / ".icons" / f"{icon}.svg"


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


def is_url(path: str) -> bool:
    return path.startswith(("http:/", "https:/", "www."))


if __name__ == "__main__":
    strings = groupby_first_letter([str(i) for i in range(1000)])
    print(strings)
