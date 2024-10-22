from __future__ import annotations

from typing import TYPE_CHECKING, Any

from mknodes.utils import log


if TYPE_CHECKING:
    import markdown


logger = log.get_logger(__name__)


class CustomFence:
    """Formatter wrapper."""

    def __init__(self, extensions: list[str]):
        self.extensions = extensions

    def custom_formatter(
        self,
        source: str,
        language: str,
        css_class: str,
        options: dict[str, str],
        md: markdown.Markdown,
        classes: list[str] | None = None,
        id_value: str = "",
        attrs: dict[str, str] | None = None,
        **kwargs: Any,
    ):
        # import mknodes as mk

        # node_kls = getattr(mk, language)
        print(f"{language=} {css_class=} {options=} {classes=} {id_value=} {attrs=}")
        try:
            return md.convert(source, **kwargs)
        except Exception:
            logger.exception("Error for custom fence %s", language)
            raise


def generate_fences() -> list[dict[str, Any]]:
    import mknodes as mk

    dcts: list[dict[str, Any]] = []
    for node_name in mk.__all__:
        dct: dict[str, Any] = {
            "name": node_name,
            "class": node_name,
            "format": fence.custom_formatter,
        }
        dcts.append(dct)
    return dcts


if __name__ == "__main__":
    from mknodes.mdlib import mdconverter

    fence = CustomFence(extensions=[])
    fences = generate_fences()
    md = mdconverter.MdConverter(extensions=["attr_list"], custom_fences=fences)
    text = "```{.MkText shift_header_levels=1}\ntest\n```"
    result = md.convert(text)
    print(result)
