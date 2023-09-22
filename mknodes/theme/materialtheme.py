from __future__ import annotations

from collections.abc import MutableMapping
import dataclasses
import functools
import pathlib

from typing import Literal

from mknodes.basenodes import mknode
from mknodes.data import datatypes
from mknodes.theme import mkblog, theme
from mknodes.theme.material import palette
from mknodes.utils import helpers, log, pathhelpers, reprhelpers


logger = log.get_logger(__name__)


COLORS = {
    "red": {"color": "#ef5552", "text": "#ffffff"},
    "pink": {"color": "#e92063", "text": "#ffffff"},
    "purple": {"color": "#ab47bd", "text": "#ffffff"},
    "deep purple": {"color": "#7e56c2", "text": "#ffffff"},
    "indigo": {"color": "#4051b5", "text": "#ffffff"},
    "blue": {"color": "#2094f3", "text": "#ffffff"},
    "light blue": {"color": "#02a6f2", "text": "#ffffff"},
    "cyan": {"color": "#00bdd6", "text": "#ffffff"},
    "teal": {"color": "#009485", "text": "#ffffff"},
    "green": {"color": "#4cae4f", "text": "#ffffff"},
    "light green": {"color": "#8bc34b", "text": "#ffffff"},
    "lime": {"color": "#cbdc38", "text": "#000000"},
    "yellow": {"color": "#ffec3d", "text": "#000000"},
    "amber": {"color": "#ffc105", "text": "#000000"},
    "orange": {"color": "#ffa724", "text": "#000000"},
    "deep orange": {"color": "#ff6e42", "text": "#ffffff"},
    "brown": {"color": "#795649", "text": "#ffffff"},
    "grey": {"color": "#757575", "text": "#ffffff"},
    "blue grey": {"color": "#546d78", "text": "#ffffff"},
    "black": {"color": "#000000", "text": "#ffffff"},
    "white": {"color": "#ffffff", "text": "#000000"},
    "custom": {"color": "#000000", "text": "#FFFFFF"},
}


IconTypeStr = Literal[
    "footnotes",
    "details",
    "previous_tab",
    "next_tab",
    "tasklist",
    "tasklist_checked",
]

ICON_TYPE: dict[IconTypeStr, str] = dict(
    footnotes="md-footnotes-icon",
    details="md-details-icon",
    previous_tab="md-tabbed-icon--prev",
    next_tab="md-tabbed-icon--next",
    tasklist="md-tasklist-icon",
    tasklist_checked="md-tasklist-icon--checked",
)


def build_badge(icon: str, text: str = "", typ: str = ""):
    classes = f"mdx-badge mdx-badge--{typ}" if typ else "mdx-badge"
    lines = [f'<span class="{classes}">']
    if icon:
        lines.append(f'<span class="mdx-badge__icon">{icon}</span>')
    if text:
        lines.append(f'<span class="mdx-badge__icon">{text}</span>')
    lines.append("</span>")
    return "".join(lines)


@dataclasses.dataclass
class AdmonitionType:
    name: str
    svg: str
    header_color: str
    icon_color: str
    border_color: str


@dataclasses.dataclass
class StatusIcon:
    name: str
    svg: str


@dataclasses.dataclass
class ColorTheme:
    color: str
    light_shade: str | None = None
    dark_shade: str | None = None

    @property
    def color_str(self) -> str:
        return helpers.get_color_str(self.color)

    @property
    def light_str(self) -> str:
        return helpers.get_color_str(self.light_shade or self.color)

    @property
    def dark_str(self) -> str:
        return helpers.get_color_str(self.dark_shade or self.color)


def get_partial_path(partial: str) -> pathlib.Path:
    import material

    path = pathlib.Path(material.__path__[0])
    return path / "partials" / f"{partial}.html"


class MaterialTheme(theme.Theme):
    """Material Theme."""

    name = "material"
    css_template = "material_css.jinja"

    def __init__(self, **kwargs):
        super().__init__(self.name, **kwargs)
        self.main_template = self.templates["main.html"]
        self._foreground_color = None
        self.blog = mkblog.MkBlog()
        self.features = self.data.get("features")
        self.show_annotation_numbers = True
        self.classic_admonition_style = True
        self.tooltip_width: int | None = None
        self.content_area_width: int | None = None
        self.default_icons = {}
        self.status_icons = []
        self.accent_fg_color = None
        self.primary_bg_color = None
        self.admonitions = []
        self.color_theme = None

    def get_template_context(self):
        return dict(
            admonitions=self.admonitions,
            show_annotation_numbers=self.show_annotation_numbers,
            classic_admonition_style=self.classic_admonition_style,
            tooltip_width=self.tooltip_width,
            content_area_width=self.content_area_width,
            default_icons=self.default_icons,
            status_icons=self.status_icons,
            accent_fg_color=self.accent_fg_color,
            primary_bg_color=self.primary_bg_color,
            color_theme=self.color_theme,
        )

    def __repr__(self):
        return reprhelpers.get_repr(self)

    @functools.cached_property
    def palettes(self) -> list[palette.Palette]:
        data = self.data.get("palette")
        if not data:
            return [palette.Palette()]
        if isinstance(data, dict):
            data = [data]
        return [
            palette.Palette(
                primary=pal.get("primary", "indigo"),
                accent=pal.get("accent", "indigo"),
                scheme=pal.get("scheme", "default"),
                media=pal.get("media"),
                toggle_name=pal.get("toggle", {}).get("name"),
                toggle_icon=pal.get("toggle", {}).get("icon"),
            )
            for pal in data
        ]

    def iter_nodes(self):
        if isinstance(self.announcement_bar, mknode.MkNode):
            yield 0, self.announcement_bar

    @property
    def announcement_bar(self):
        return self.main_template.announcement_bar

    @announcement_bar.setter
    def announcement_bar(self, value):
        if isinstance(value, mknode.MkNode):
            value.associated_project = self.associated_project
        self.main_template.announcement_bar = value

    def get_accent_color(self) -> str:
        # sourcery skip: use-or-for-fallback
        color = self._get_color("accent", fallback="")
        if not color:
            color = self._get_color("primary", fallback="indigo")
        return COLORS[color]["color"]

    def _get_color(self, color_type: Literal["primary", "accent"], fallback: str) -> str:
        pal = self.palettes[0]
        match color_type:
            case "primary":
                return pal.primary or fallback
            case "accent":
                return pal.accent or fallback

    def set_color(self, color_type: Literal["primary", "accent"], value: str):
        pal = self.palettes[0]
        match color_type:
            case "primary":
                pal.primary = value
            case "accent":
                pal.accent = value

    def set_accent_foreground_color(self, color: datatypes.RGBColorType):
        color_str = helpers.get_color_str(color)
        self.accent_fg_color = color_str
        self.set_color("accent", "custom")
        return color_str

    def set_primary_background_color(
        self,
        color: datatypes.RGBColorType,
    ):
        self.set_color("primary", "custom")
        color_str = helpers.get_color_str(color)
        self.primary_bg_color = color_str
        return color_str

    @property
    def primary_color(self) -> str:
        if self._foreground_color:
            return self._foreground_color
        color = self._get_color("primary", fallback="indigo")
        return COLORS[color]["color"]

    @property
    def _text_color(self):
        color = self._get_color("primary", fallback="indigo")
        return COLORS[color]["text"]

    def add_admonition_type(
        self,
        name: str,
        material_icon: str,
        header_color: datatypes.ColorType,
        icon_color: datatypes.ColorType | None = None,
        border_color: datatypes.ColorType | None = None,
    ):
        header_col_str = helpers.get_color_str(header_color)
        icon_col_str = helpers.get_color_str(icon_color or (255, 255, 255))
        border_col_str = helpers.get_color_str(border_color or (255, 255, 255))
        icon = pathhelpers.get_material_icon_path(material_icon)
        data = icon.read_text()
        adm = AdmonitionType(name, data, header_col_str, icon_col_str, border_col_str)
        self.admonitions.append(adm)

    def set_primary_foreground_color(
        self,
        color: datatypes.ColorType,
        light_shade: datatypes.ColorType | None = None,
        dark_shade: datatypes.ColorType | None = None,
    ):
        self._foreground_color = color
        self.set_color("primary", "custom")
        if light_shade is None:
            light_shade = color
        if dark_shade is None:
            dark_shade = color
        color_str = helpers.get_color_str(color)
        self.color_theme = ColorTheme(
            color_str,
            helpers.get_color_str(light_shade),
            helpers.get_color_str(dark_shade),
        )
        return color_str

    def set_default_icon(self, icon_type: IconTypeStr, data: str):
        self.default_icons[icon_type] = data

    def add_status_icon(self, name: str, material_icon: str):
        icon = pathhelpers.get_material_icon_path(material_icon)
        data = icon.read_text()
        self.status_icons.append(StatusIcon(name, data))

    def adapt_extensions(self, extensions: MutableMapping[str, dict]):
        for k in dict(extensions).copy():
            if k == "pymdownx.emoji":
                from materialx import emoji

                extensions[k].update(
                    {
                        "emoji_index": emoji.twemoji,
                        "emoji_generator": emoji.to_svg,
                    },
                )
            elif k in ["pymdownx.blocks.tab", "pymdownx.tabbed"]:
                extensions[k]["alternate_style"] = True
            elif k == "pymdownx.tasklist":
                extensions[k]["custom_checkbox"] = True


if __name__ == "__main__":
    from mknodes import project

    theme = MaterialTheme()
    proj = project.Project.for_mknodes()
