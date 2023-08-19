from __future__ import annotations

import markdown

from mknodes.basenodes import mknode
from mknodes.pages import templateblocks
from mknodes.utils import helpers


BLOCK = """{{% block {block_name} %}}
{pre_block}
{super_block}
{post_block}
{{% endblock %}}
"""


class PageTemplate:
    def __init__(
        self,
        md: markdown.Markdown,
        filename: str,
        extends: str | None = "base",
    ):
        self.filename = filename
        self.data: dict[templateblocks.BlockStr, dict[str, str | mknode.MkNode]] = {}
        self.extends = extends
        self.md = md

    def __repr__(self):
        return helpers.get_repr(
            self,
            filename=self.filename,
            extends=self.extends if self.extends != "base" else None,
            _filter_empty=True,
        )

    @property
    def announcement_bar(self):
        return dct.get("replace") if (dct := self.data.get("announce")) else None

    @announcement_bar.setter
    def announcement_bar(self, value):
        self._replace_block("announce", value, convert_markdown=True)

    @property
    def content(self):
        return dct.get("replace") if (dct := self.data.get("content")) else None

    @content.setter
    def content(self, value):
        self._replace_block("content", value, convert_markdown=True)

    def _replace_block(
        self,
        block: templateblocks.BlockStr,
        text: str | mknode.MkNode,
        convert_markdown: bool = False,
    ):
        if not isinstance(text, mknode.MkNode):
            value = self.md.convert(text) if convert_markdown else text
        else:
            value = text
        self.data.setdefault(block, {})["replace"] = value

    def _insert_before_block(
        self,
        block: templateblocks.BlockStr,
        text: str | mknode.MkNode,
        convert_markdown: bool = False,
    ):
        if not isinstance(text, mknode.MkNode):
            value = self.md.convert(text) if convert_markdown else text
        else:
            value = text
        self.data.setdefault(block, {})["before"] = value

    def _insert_after_block(
        self,
        block: templateblocks.BlockStr,
        text: str | mknode.MkNode,
        convert_markdown: bool = False,
    ):
        if not isinstance(text, mknode.MkNode):
            value = self.md.convert(text) if convert_markdown else text
        else:
            value = text
        self.data.setdefault(block, {})["after"] = value

    def build_html(self) -> str | None:
        blocks = ['{% extends "' + self.extends + '.html" %}\\n'] if self.extends else []
        if not self.data:
            return None
        for k, v in self.data.items():
            if "replace" in v:
                pre = v["replace"]
                if isinstance(pre, mknode.MkNode):
                    pre = self.md.convert(str(pre))
                b = BLOCK.format(
                    block_name=k,
                    pre_block=pre,
                    super_block="",
                    post_block="",
                )
                blocks.append(b)
            elif "before" in v or "after" in v:
                pre = v.get("before", "")
                post = v.get("after", "")
                if isinstance(pre, mknode.MkNode):
                    pre = self.md.convert(str(pre))
                if isinstance(post, mknode.MkNode):
                    post = self.md.convert(str(post))
                b = BLOCK.format(
                    block_name=k,
                    pre_block=str(pre),
                    super_block="{{ super() }}",
                    post_block=str(post),
                )
                blocks.append(b)
        return "\n".join(blocks) + "\n"


if __name__ == "__main__":
    import mknodes

    from mknodes import mkdocsconfig

    cfg = mkdocsconfig.Config()
    md = cfg.get_markdown_instance()
    manager = PageTemplate(md, filename="main.html")
    manager._insert_after_block(
        "announce",
        mknodes.MkAdmonition("test"),
        convert_markdown=True,
    )
    html = manager.build_html()
    print(html)
