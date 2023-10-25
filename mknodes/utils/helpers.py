from __future__ import annotations

from collections.abc import Callable, Generator, Iterable, Sequence
import itertools
import os
import re

from typing import Any, Literal, ParamSpec, TypeVar

from mknodes.utils import log


logger = log.get_logger(__name__)


T = TypeVar("T")


def reduce_list(data_set: Iterable[T]) -> list[T]:
    """Reduce duplicate items in a list and preserve order."""
    return list(dict.fromkeys(data_set))


def get_hash(obj: Any) -> str:
    import hashlib

    hash_md5 = hashlib.md5(str(obj).encode("utf-8"))
    return hash_md5.hexdigest()[:7]


def get_color_str(data: str | tuple) -> str:  # type: ignore[return]
    import coloraide

    rgb_tuple_len = 3

    match data:
        case str():
            return coloraide.Color(data).to_string()
        case tuple() if len(data) == rgb_tuple_len:
            color = coloraide.Color("srgb", [i / 255 for i in data])
            return color.to_string(comma=True)
        case tuple():
            color = coloraide.Color("srgb", [i / 255 for i in data[:3]], data[3])
            return color.to_string(comma=True)
        case _:
            raise TypeError(data)


def extract_header_section(markdown: str, section_name: str) -> str | None:
    """Extract block with given header from markdown."""
    header_pattern = re.compile(f"^(#+) {section_name}$", re.MULTILINE)
    header_match = header_pattern.search(markdown)
    if header_match is None:
        return None
    section_level = len(header_match[1])
    start_index = header_match.span()[1] + 1
    end_pattern = re.compile(f"^#{{1,{section_level}}} ", re.MULTILINE)
    end_match = end_pattern.search(markdown[start_index:])
    if end_match is None:
        return markdown[start_index:]
    end_index = end_match.span()[0]
    return markdown[start_index : end_index + start_index]


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
    return re.sub("^[^0-9a-zA-Z_#]+", "", text)


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
    align: Literal["left", "right", "center"] | None = None,
) -> str:
    """Apply styling to given markdown.

    Arguments:
        text: Text to style
        size: Optional text size
        bold: Whether styled text should be bold
        italic: Whether styled text should be italic
        code: Whether styled text should styled as (inline) code
        align: Optional text alignment
    """
    if size:
        text = f"<font size='{size}'>{text}</font>"
    if bold:
        text = f"**{text}**"
    if italic:
        text = f"*{text}*"
    if code:
        text = f"`{text}`"
    if align:
        text = f"<p style='text-align: {align};'>{text}</p>"
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


def get_output_from_call(
    call: str | Sequence[str],
    cwd: str | os.PathLike | None,
) -> str | None:
    import subprocess

    if not isinstance(call, str):
        call = " ".join(call)
    try:
        return subprocess.run(
            call,
            stdout=subprocess.PIPE,
            text=True,
            shell=True,
            cwd=cwd,
        ).stdout
    except subprocess.CalledProcessError:
        logger.warning("Executing %s failed", call)
        return None


P = ParamSpec("P")
R = TypeVar("R")


def list_to_tuple(fn: Callable[P, R]) -> Callable[P, R]:
    """Decorater to convert lists to tuples in the arguments."""

    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        safe_args = [tuple(item) if isinstance(item, list) else item for item in args]
        if kwargs:
            kwargs = {
                key: tuple(value) if isinstance(value, list) else value
                for key, value in kwargs.items()
            }  # type: ignore[assignment]
        return fn(*safe_args, **kwargs)  # type: ignore[arg-type]

    return wrapper


if __name__ == "__main__":
    strings = groupby_first_letter([str(i) for i in range(1000)])
    print(strings)
