from __future__ import annotations

import markdown

from mknodes.utils import log


logger = log.get_logger(__name__)


class CustomFence:
    """Formatter wrapper."""

    def __init__(self, extensions: list):
        self.extensions = extensions

    def custom_formatter(
        self,
        source,
        language,
        css_class,
        options,
        md: markdown.Markdown,
        classes=None,
        id_value="",
        attrs=None,
        **kwargs,
    ):
        # import mknodes as mk

        # node_kls = getattr(mk, language)
        # print(f"{language=} {css_class=} {options=} {classes=} {id_value=} {attrs=}")
        try:
            return md.convert(source)
        except Exception:
            logger.exception("Error for custom fence %s", language)
            raise


def generate_fences():
    import mknodes as mk

    dcts = []
    for node_name in mk.__all__:
        dct = {"name": node_name, "class": node_name, "format": fence.custom_formatter}
        dcts.append(dct)
    return dcts


if __name__ == "__main__":
    fence = CustomFence(extensions=[])
    fence_dct = {"name": "ab", "class": "ab", "format": fence.custom_formatter}
    config = {"custom_fences": generate_fences()}
    md = markdown.Markdown(
        extensions=["pymdownx.superfences", "attr_list"],
        extension_configs={"pymdownx.superfences": config},
    )
    text = "```{.MkText shift_header_levels=1}\ntest\n```"
    result = md.convert(text)
    print(result)
