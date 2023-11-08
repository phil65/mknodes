from __future__ import annotations

from collections.abc import MutableMapping
from typing import Any

import jinjarope

from mknodes.data import admonition, datatypes
from mknodes.info import contexts
from mknodes.pages import templateblocks, templateregistry
from mknodes.utils import color, icons, log, reprhelpers, resources


logger = log.get_logger(__name__)


class Theme:
    """MkDocs Theme."""

    css_template = "css/theme_mkdocs.css"

    def __init__(
        self,
        name: str,
        *,
        data: dict[str, Any] | None = None,
    ):
        """Instanciate the theme.

        Arguments:
            name: The theme name
            data: Additional data for the theme
        """
        self.name = name
        self.data = data or {}
        self.features = self.data.get("features")
        loader = jinjarope.registry.get_package_loader("mknodes.resources")
        self.env = jinjarope.Environment(loader=loader)
        self.templates = templateregistry.TemplateRegistry()
        self.main_template = self.templates["main.html"]
        self.error_page = self.templates["404.html"]

        self.alternating_table_colors = False

        self.admonitions: list[admonition.AdmonitionType] = []
        self.add_admonition_type(
            name="theme",
            icon="mdi:file",
            header_color=self.primary_color,
            icon_color="black",
            border_color="black",
            font_color=self.text_color,
        )

    def __repr__(self):
        return reprhelpers.get_repr(self, name=self.name)

    def add_admonition_type(
        self,
        name: str,
        icon: str,
        header_color: datatypes.ColorType,
        icon_color: datatypes.ColorType | None = None,
        border_color: datatypes.ColorType | None = None,
        font_color: datatypes.ColorType | None = None,
    ):
        """Add a custom admonition type.

        Arguments:
            name: Slug for new admonition type
            icon: Either a Pyconify icon key or an <svg> element
            header_color: Color for the admonition header
            icon_color: Color for the admonition icon
            border_color: Color for the admonition border
            font_color: Color for the admonition header font
        """
        header_col_str = str(color.Color(header_color))
        icon_col_str = str(color.Color(icon_color or (255, 255, 255)))
        border_col_str = str(color.Color(border_color or (255, 255, 255)))
        font_col_str = str(color.Color(font_color or (255, 255, 255)))
        adm = admonition.AdmonitionType(
            name=name,
            svg=icons.get_icon_svg(icon) if not icon.startswith("<") else icon,
            header_color=header_col_str,
            icon_color=icon_col_str,
            border_color=border_col_str,
            font_color=font_col_str,
        )
        self.admonitions.append(adm)

    def get_resources(self) -> resources.Resources:
        """Return resources required for the theme.

        Usually, the resources consist of static templates and CSS.
        """
        req: list[resources.CSSFile | resources.CSSText] = []
        if self.css_template:
            tmpl_ctx = self.get_css_context()
            css_text = self.env.render_template(self.css_template, variables=tmpl_ctx)
            req = [resources.CSSText(content=css_text, filename="mknodes_theme.css")]
        return resources.Resources(css=req)

    def get_css_context(self) -> dict[str, Any]:
        """Return variables used to resolve the CSS template.

        Can be overridden by subclasses.
        """
        return dict(
            admonitions=self.admonitions,
            primary_color=self.primary_color,
            text_color=self.text_color,
            alternating_table_colors=self.alternating_table_colors,
            css_primary_fg=self.text_color,
            css_primary_bg=self.primary_color,
            css_primary_bg_light=self.primary_color,
            css_accent_fg=self.text_color,
            css_accent_fg_transparent=self.text_color,
            css_accent_bg=self.primary_color,
            css_default_fg="#222222",
            css_default_bg="#DDDDDD",
        )

    @property
    def context(self):
        ctx = self.get_css_context()
        return contexts.ThemeContext(
            name=self.name,
            data=self.data,
            primary_color=self.primary_color,
            text_color=self.text_color,
            admonitions=self.admonitions,
            css_primary_fg=ctx["css_primary_fg"],
            css_primary_bg=ctx["css_primary_bg"],
            css_primary_bg_light=ctx["css_primary_bg_light"],
            css_accent_fg=ctx["css_accent_fg"],
            css_accent_fg_transparent=ctx["css_accent_fg_transparent"],
            css_accent_bg=ctx["css_accent_bg"],
            css_default_fg=ctx["css_default_fg"],
            css_default_bg=ctx["css_default_bg"],
        )

    @classmethod
    def get_theme(
        cls,
        theme_name: str = "material",
        data: dict[str, Any] | None = None,
        **kwargs: Any,
    ):
        """Return theme instance of corresponding subclass based on theme name.

        Arguments:
            theme_name: Name of the theme
            data: Additional data for the theme
            kwargs: Additional keyword arguments passe to the Theme
        """
        if theme_name == "material":
            import mknodes as mk

            return mk.MaterialTheme(data=data, **kwargs)
        return Theme(theme_name, data=data, **kwargs)

    def iter_nodes(self):
        import mknodes as mk

        for block in self.main_template.blocks:
            if not isinstance(block, templateblocks.HtmlBlock):
                continue
            for node in block.items:
                if not isinstance(node, mk.MkNode):
                    continue
                yield 0, node

    @property
    def primary_color(self) -> str:
        """Return the primary color of the theme.

        Can be overridden by subclasses.
        """
        return "#2fa4e7"

    @property
    def text_color(self) -> str:
        """Return the text color of the theme.

        Can be overridden by subclasses.
        """
        return "#333333"

    def adapt_extensions(self, extensions: MutableMapping[str, dict]):
        """Make adaptions to markdown extensions for the theme if required.

        Arguments:
            extensions: The extensions to adapt
        """
        if self.name.lower() != "mkdocs":
            return
        for k in dict(extensions).copy():
            ext = extensions[k]
            if k == "pymdownx.highlight":
                # default style "table" looks broken with mkdocs
                ext["linenums_style"] = "inline"  # pymdownx-inline

    def adapt_extras(self, extras: dict):
        """Adapt the "extras" dictionary containing additional information."""

    @property
    def template_path(self) -> str:
        """Return the template directory."""
        from mkdocs import utils

        return utils.get_theme_dir(self.name)


if __name__ == "__main__":
    theme = Theme.get_theme("material")
    print(theme)
