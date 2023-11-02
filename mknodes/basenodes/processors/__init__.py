from __future__ import annotations

from mknodes.utils import log
import re
from typing import TYPE_CHECKING
import textwrap
from mknodes.pages.metadata import Metadata


if TYPE_CHECKING:
    import mknodes as mk

HEADER_REGEX = re.compile(r"^(#{1,6}) (.*)", flags=re.MULTILINE)

logger = log.get_logger(__name__)


class TextProcessor:
    ID: str

    def run(self, text: str) -> str:
        raise NotImplementedError


class AnnotationProcessor(TextProcessor):
    ID = "annotations"

    def __init__(self, item):
        self.item = item

    def run(self, text: str) -> str:
        return self.item.attach_annotations(text) if self.item.annotations else text


class FootNotesProcessor(TextProcessor):
    ID = "footnotes"

    def __init__(self, item):
        self.item = item

    def run(self, text: str) -> str:
        return f"{text}\n\n{self.item.footnotes}" if self.item.footnotes else text


class IndentationProcessor(TextProcessor):
    ID = "indentation"

    def __init__(self, indent: int | str = 4):
        self.indent = " " * indent if isinstance(indent, int) else indent

    def run(self, text: str) -> str:
        return textwrap.indent(text, self.indent) if self.indent else text


class ShiftHeaderLevelProcessor(TextProcessor):
    ID = "shift_header_levels"

    def __init__(self, level_shift):
        self.level_shift = level_shift

    def run(self, text: str) -> str:
        if not self.level_shift:
            return text

        def mod_header(match: re.Match, levels: int) -> str:
            header_str = match[1]
            if levels > 0:
                header_str += levels * "#"
            else:
                header_str = header_str[:levels]
            return f"{header_str} {match[2]}"

        return re.sub(HEADER_REGEX, lambda x: mod_header(x, self.level_shift), text)


class RenderJinjaProcessor(TextProcessor):
    ID = "render_jinja_templates"

    def __init__(self, env, variables=None):
        self.env = env
        self.variables = variables or {}

    def run(self, text: str) -> str:
        return self.env.render(text, self.variables)


class AppendCssClassesProcessor(TextProcessor):
    ID = "append_css_classes"

    def __init__(self, item):
        self.item = item

    def run(self, text: str) -> str:
        return self.item.attach_css_classes(text) if self.item.mods.css_classes else text


class PrependMetadataProcessor(TextProcessor):
    ID = "prepend_metadata"

    def __init__(self, meta: mk.MkPage | Metadata):
        self.meta = meta if isinstance(meta, Metadata) else meta.resolved_metadata

    def run(self, text: str) -> str:
        header = self.meta.as_page_header()
        return f"{header}\n{text}" if header else text


class PrependHeaderProcessor(TextProcessor):
    ID = "prepend_header"

    def __init__(self, header: str | None):
        self.header = header

    def run(self, text: str) -> str:
        if not self.header:
            return text
        header = self.header if self.header.startswith("#") else f"## {self.header}"
        return f"{header}\n\n{text}"


if __name__ == "__main__":
    text = "## test"
    processor = ShiftHeaderLevelProcessor(3)
    text = processor.run(text)
    print(text)
