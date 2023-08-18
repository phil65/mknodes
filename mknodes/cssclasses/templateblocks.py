from __future__ import annotations

from typing import Literal

from mknodes.basenodes import mknode


BlockStr = Literal[
    "analytics",
    "announce",
    "config",
    "container",
    "content",
    "extrahead",
    "fonts",
    "footer",
    "header",
    "hero",
    "htmltitle",
    "libs",
    "outdated",
    "scripts",
    "site_meta",
    "site_nav",
    "styles",
    "tabs",
]


BLOCK = """{{% block {block_name} %}}
{pre_block}
{super_block}
{post_block}
{{% endblock %}}
"""


class BlockManager:
    def __init__(self, md):
        self.data: dict[BlockStr, dict[str, str | mknode.MkNode]] = {}
        self.md = md

    def replace_block(
        self,
        block: BlockStr,
        text: str | mknode.MkNode,
        convert_markdown: bool = False,
    ):
        if not isinstance(text, mknode.MkNode):
            value = self.md.convert(text) if convert_markdown else text
        else:
            value = text
        self.data.setdefault(block, {})["replace"] = value

    def insert_before_block(
        self,
        block: BlockStr,
        text: str | mknode.MkNode,
        convert_markdown: bool = False,
    ):
        if not isinstance(text, mknode.MkNode):
            value = self.md.convert(text) if convert_markdown else text
        else:
            value = text
        self.data.setdefault(block, {})["before"] = value

    def insert_after_block(
        self,
        block: BlockStr,
        text: str | mknode.MkNode,
        convert_markdown: bool = False,
    ):
        if not isinstance(text, mknode.MkNode):
            value = self.md.convert(text) if convert_markdown else text
        else:
            value = text
        self.data.setdefault(block, {})["after"] = value

    def build_main_html(self) -> str | None:
        blocks = [r'{% extends "base.html" %}\n']
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
    manager = BlockManager(md)
    manager.insert_after_block(
        "announce",
        mknodes.MkAdmonition("test"),
        convert_markdown=True,
    )
    html = manager.build_main_html()
    print(html)
