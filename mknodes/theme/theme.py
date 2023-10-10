from __future__ import annotations

from collections.abc import MutableMapping
import dataclasses

from typing import Any

from mknodes import project
from mknodes.data import datatypes
from mknodes.info import contexts
from mknodes.pages import templateblocks, templateregistry
from mknodes.utils import helpers, icons, log, reprhelpers, resources


logger = log.get_logger(__name__)


@dataclasses.dataclass
class AdmonitionType:
    name: str
    svg: str
    header_color: str
    icon_color: str
    border_color: str
    font_color: str


class Theme:
    """MkDocs Theme."""

    css_template = "css/theme_mkdocs.css"

    def __init__(
        self,
        theme_name: str,
        *,
        data: dict[str, Any] | None = None,
        project: project.Project | None = None,
        template_registry: templateregistry.TemplateRegistry | None = None,
    ):
        self.associated_project = project

        self.theme_name = theme_name
        self.data = data or {}
        self.features = self.data.get("features")

        self.templates = template_registry or templateregistry.TemplateRegistry()
        self.main_template = self.templates["main.html"]
        self.error_page = self.templates["404.html"]

        self.admonitions: list[AdmonitionType] = []
        self.add_admonition_type(
            name="theme",
            material_icon="file",
            header_color=self.primary_color,
            icon_color="black",
            border_color="black",
            font_color=self.text_color,
        )

    def __repr__(self):
        return reprhelpers.get_repr(self, theme_name=self.theme_name)

    def add_admonition_type(
        self,
        name: str,
        material_icon: str,
        header_color: datatypes.ColorType,
        icon_color: datatypes.ColorType | None = None,
        border_color: datatypes.ColorType | None = None,
        font_color: datatypes.ColorType | None = None,
    ):
        """Add a custom admonition type.

        Arguments:
            name: Slug for new admonition type
            material_icon: Material icon path
            header_color: Color for the admonition header
            icon_color: Color for the admonition icon
            border_color: Color for the admonition border
            font_color: Color for the admonition header font
        """
        header_col_str = helpers.get_color_str(header_color)
        icon_col_str = helpers.get_color_str(icon_color or (255, 255, 255))
        border_col_str = helpers.get_color_str(border_color or (255, 255, 255))
        font_col_str = helpers.get_color_str(border_color or (255, 255, 255))
        adm = AdmonitionType(
            name=name,
            svg=icons.get_icon_svg(material_icon),
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
        if self.css_template and (proj := self.associated_project):
            tmpl_ctx = self.get_template_context()
            css_text = proj.context.env.render_template(
                self.css_template,
                variables=tmpl_ctx,
            )
            req = [resources.CSSText(content=css_text, filename="mknodes_theme.css")]
        return resources.Resources(css=req, templates=list(self.templates))

    def get_template_context(self) -> dict[str, Any]:
        """Return variables used to resolve the CSS template.

        Can be overridden by subclasses.
        """
        return dict(
            admonitions=self.admonitions,
            primary_color=self.primary_color,
            text_color=self.text_color,
            css_primary_fg=self.text_color,
            css_primary_bg=self.primary_color,
            css_primary_bg_light=self.primary_color,
            css_accent_fg=self.text_color,
            css_accent_fg_transparent=self.text_color,
            css_accent_bg=self.primary_color,
            css_default_fg="#222222",
            css_default_bg="#DDDDDD",
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
            from mknodes.theme import materialtheme

            return materialtheme.MaterialTheme(data=data, **kwargs)
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

    @property
    def context(self):
        ctx = self.get_template_context()
        return contexts.ThemeContext(
            name=self.theme_name,
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

    def adapt_extensions(self, extensions: MutableMapping[str, dict]):
        pass


if __name__ == "__main__":
    theme = Theme.get_theme("material")
    proj = project.Project.for_mknodes()
    print(theme)
