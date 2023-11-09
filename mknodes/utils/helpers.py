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
    """Reduce duplicate items in a list and preserve order.

    Arguments:
        data_set: The Iterable to reduce.
    """
    return list(dict.fromkeys(data_set))


def get_hash(obj: Any) -> str:
    """Get a Md5 hash for given object.

    Arguments:
        obj: The object to get a hash for
    """
    import hashlib

    hash_md5 = hashlib.md5(str(obj).encode("utf-8"))
    return hash_md5.hexdigest()[:7]


def extract_header_section(markdown: str, section_name: str) -> str | None:
    """Extract block with given header from markdown.

    Arguments:
        markdown: The markdown to extract a section from
        section_name: The header of the section to extract
    """
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


def groupby(
    data: Iterable[T],
    keyfunc: Callable | None = None,
    sort_groups: bool = True,
    natural_sort: bool = False,
    reverse: bool = False,
) -> dict[str, list[T]]:
    """Group given iterable using given group function.

    Arguments:
        data: Iterable to group
        keyfunc: Sort function
        sort_groups: Whether to sort the groups
        natural_sort: Whether to use a natural sort algorithm
        reverse: Whether to reverse the value list
    """
    if keyfunc is None:

        def keyfunc(x):
            return x

    if sort_groups:
        if natural_sort:
            import natsort

            data = natsort.natsorted(data, key=keyfunc)
        else:
            data = sorted(data, key=keyfunc)
    if reverse:
        data = reversed(list(data))
    return {k: list(g) for k, g in itertools.groupby(data, keyfunc)}


def groupby_first_letter(
    data: Iterable[T],
    keyfunc: Callable | None = None,
) -> dict[str, list[T]]:
    """Group given iterable by first letter.

    Arguments:
        data: Iterable to group
        keyfunc: Optional alternative sort function
    """
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
    """Batch data into tuples of length n. The last batch may be shorter.

    Examples:
        ``` py
        batched('ABCDEFG', 3)  # returns ABC DEF G
        ```

    Arguments:
        iterable: The iterable to yield as batches
        n: The batch size
    """
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


def is_url(string: str) -> bool:
    """Return true when given string represents a HTTP url.

    Arguments:
        string: The string to check
    """
    return string.startswith(("http:/", "https:/", "www."))


def get_output_from_call(
    call: str | Sequence[str],
    cwd: str | os.PathLike | None,
) -> str | None:
    """Execute a system call and return the captured stdout.

    call: The system call to execute
    cwd: The working directory for the call. If None use cwd.
    """
    import subprocess

    if not isinstance(call, str):
        call = " ".join(call)
    msg = f"Executing {call!r}..."
    logger.info(msg)
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
    """Decorator to convert lists to tuples in the arguments.

    Arguments:
        fn: The function to decorate
    """

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
