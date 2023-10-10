from __future__ import annotations

from collections.abc import MutableMapping
import dataclasses
import functools
import pathlib

from typing import Any, Literal

from mknodes.data import datatypes
from mknodes.theme import colortheme, theme
from mknodes.theme.material import palette
from mknodes.utils import helpers, icons, log, reprhelpers


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
    "custom": {"color": "#4051b5", "text": "#ffffff"},
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


@dataclasses.dataclass
class StatusIcon:
    name: str
    svg: str


class MaterialTheme(theme.Theme):
    """Material Theme."""

    name = "material"
    css_template = "css/theme_material.css"

    def __init__(self, **kwargs):
        self._foreground_color = None
        self.show_annotation_numbers = False
        self.classic_admonition_style = True
        self.alternating_table_colors = False
        self.tooltip_width: int | None = None
        self.content_area_width: int | None = None
        self.default_icons = {}
        self.status_icons = []
        self.accent_fg_color = None
        self.primary_bg_color = None
        self.color_theme = None
        super().__init__(self.name, **kwargs)

    def get_template_context(self) -> dict[str, Any]:
        """Return template context (used to render the CSS template."""
        return dict(
            admonitions=self.admonitions,
            show_annotation_numbers=self.show_annotation_numbers,
            classic_admonition_style=self.classic_admonition_style,
            alternating_table_colors=self.alternating_table_colors,
            tooltip_width=self.tooltip_width,
            content_area_width=self.content_area_width,
            default_icons=self.default_icons,
            status_icons=self.status_icons,
            accent_fg_color=self.accent_fg_color,
            primary_bg_color=self.primary_bg_color,
            color_theme=self.color_theme,
            css_primary_fg="var(--md-primary-fg-color)",
            css_primary_bg="var(--md-primary-bg-color)",
            css_primary_bg_light="var(--md-primary-bg-color--light)",
            css_accent_fg="var(--md-accent-fg-color)",
            css_accent_fg_transparent="var(--md-accent-fg-color--transparent)",
            css_accent_bg="var(--md-accent-bg-color)",
            css_default_fg="var(--md-code-fg-color)",
            css_default_bg="var(--md-code-bg-color)",
        )

    def __repr__(self):
        return reprhelpers.get_repr(self)

    @functools.cached_property
    def palettes(self) -> list[palette.Palette]:
        """Return a list of palettes used by the theme."""
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

    def get_accent_color(self) -> str:
        """Get the accent foreground color."""
        # sourcery skip: use-or-for-fallback
        color = self._get_color("accent", fallback="")
        if not color:
            color = self._get_color("primary", fallback="indigo")
        return COLORS[color]["color"]

    def _get_color(self, color_type: Literal["primary", "accent"], fallback: str) -> str:
        """Return either primary or accent color.

        Arguments:
            color_type: The color type to get
            fallback: value to return in case color_type is not defined.
        """
        pal = self.palettes[0]
        match color_type:
            case "primary":
                return pal.primary or fallback
            case "accent":
                return pal.accent or fallback

    def _set_color(self, color_type: Literal["primary", "accent"], value: str):
        """Set the color for the first palette.

        Arguments:
            color_type: The color type to set
            value: The color to set
        """
        pal = self.palettes[0]
        match color_type:
            case "primary":
                pal.primary = value
            case "accent":
                pal.accent = value

    def set_accent_foreground_color(self, color: datatypes.RGBColorType):
        """Set the accent foreground color.

        Arguments:
            color: Color to set
        """
        color_str = helpers.get_color_str(color)
        self.accent_fg_color = color_str
        self._set_color("accent", "custom")
        return color_str

    def set_primary_background_color(
        self,
        color: datatypes.RGBColorType,
    ):
        """Set the primary background color.

        Arguments:
            color: Color to set
        """
        self._set_color("primary", "custom")
        color_str = helpers.get_color_str(color)
        self.primary_bg_color = color_str
        return color_str

    @property
    def primary_color(self) -> str:
        """Get the primary foreground color."""
        if self._foreground_color:
            return self._foreground_color
        color = self._get_color("primary", fallback="indigo")
        return COLORS[color]["color"]

    @property
    def _text_color(self) -> str:
        """Get the primary text color."""
        color = self._get_color("primary", fallback="indigo")
        return COLORS[color]["text"]

    def set_primary_foreground_color(
        self,
        color: datatypes.ColorType,
        light_shade: datatypes.ColorType | None = None,
        dark_shade: datatypes.ColorType | None = None,
    ):
        """Set a custom color theme.

        Requires primary color set to "custom".

        Arguments:
            color: Main color
            light_shade: Optional light shade. If None, same as color.
            dark_shade: Optional dark shade. If None, same as color.
        """
        self._foreground_color = color
        self._set_color("primary", "custom")
        if light_shade is None:
            light_shade = color
        if dark_shade is None:
            dark_shade = color
        color_str = helpers.get_color_str(color)
        self.color_theme = colortheme.ColorTheme(
            color_str,
            helpers.get_color_str(light_shade),
            helpers.get_color_str(dark_shade),
        )
        return color_str

    def set_default_icon(self, icon_type: IconTypeStr, data: str):
        """Allows setting some custom default icons used throughout the theme.

        Arguments:
            icon_type: Icon type to set a new default for
            data: svg for the new icon
        """
        self.default_icons[icon_type] = data

    def add_status_icon(self, name: str, material_icon: str):
        """Add a custom status icon.

        Arguments:
            name: slug for the status icon
            material_icon: Material icon name
        """
        data = icons.get_icon_svg(material_icon)
        status_icon = StatusIcon(name, data)
        self.status_icons.append(status_icon)

    def adapt_extensions(self, extensions: MutableMapping[str, dict]):
        """MkDocs-Material needs some custom configuration for extensions.

        This method will get called during the build process in order to make sure
        that theme-specifics are considered.

        Arguments:
            extensions: Extensions to adapt.
        """
        for k in dict(extensions).copy():
            ext = extensions[k]
            if k == "pymdownx.emoji":
                from materialx import emoji

                ext.update(
                    {
                        "emoji_index": emoji.twemoji,
                        "emoji_generator": emoji.to_svg,
                    },
                )
            elif k in ["pymdownx.blocks.tab", "pymdownx.tabbed"]:
                ext["alternate_style"] = True
            elif k == "pymdownx.tasklist":
                ext["custom_checkbox"] = True

    @staticmethod
    def get_partial_path(partial: str) -> pathlib.Path:
        """Return the path to the MkDocs-Material partial file.

        Arguments:
            partial: The partial to get a path for.
        """
        import material

        path = pathlib.Path(material.__path__[0])
        return path / "partials" / f"{partial.removesuffix('.html')}.html"


if __name__ == "__main__":
    from mknodes import project

    theme = MaterialTheme()
    proj = project.Project.for_mknodes()
