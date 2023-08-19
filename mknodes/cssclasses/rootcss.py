from __future__ import annotations

from typing import Literal

import coloraide

from mknodes.cssclasses import cssclasses
from mknodes.data import datatypes


RGB_TUPLE_LEN = 3

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


def wrap_svg(data):
    return f"url('data:image/svg+xml;charset=utf-8,{data}')"


def get_color_str(data: str | tuple) -> str:  # type: ignore[return]
    match data:
        case str():
            return coloraide.Color(data).to_string()
        case tuple() if len(data) == RGB_TUPLE_LEN:
            color = coloraide.Color("srgb", [i / 255 for i in data])
            return color.to_string(comma=True)
        case tuple():
            color = coloraide.Color("srgb", [i / 255 for i in data[:3]], data[3])
            return color.to_string(comma=True)
        case _:
            raise TypeError(data)


class RootCSS(cssclasses.CSS):
    PREFIX = ":root"

    def __init__(self):
        super().__init__(r":root {}")

    def set_content_area_width(self, width: int):
        self.add_rule(".md-grid", {"max-width": f"{width}px"})

    def set_tooltip_width(self, height: int):
        self[self.PREFIX]["--md-tooltip-width"] = f"{height}px"

    def set_classic_admonition_style(self):
        self.add_rule(
            ".md-typeset .admonition, .md-typeset details",
            {"border-width": 0, "border-left-width": "4px"},
        )

    def add_admonition_type(
        self,
        name: str,
        data: str,
        header_color: datatypes.ColorType,
        icon_color: datatypes.ColorType | None = None,
        border_color: datatypes.ColorType | None = None,
    ):
        self[self.PREFIX][f"--md-admonition-icon--{name}"] = wrap_svg(data)
        header_color_str = get_color_str(header_color)
        icon_color_str = get_color_str(icon_color or (255, 255, 255))
        border_color_str = get_color_str(border_color or (255, 255, 255))
        self.add_rule(
            f".md-typeset .admonition.{name}, .md-typeset details.{name}",
            {
                "border-color": border_color_str,
            },
        )
        self.add_rule(
            f".md-typeset .{name} > .admonition-title, .md-typeset .{name} > summary",
            {"background-color": header_color_str},
        )
        self.add_rule(
            f".md-typeset .{name} > .admonition-title::before, .md-typeset .{name} >"
            " summary::before",
            {
                "background-color": icon_color_str,
                "-webkit-mask-image": f"var(--md-admonition-icon--{name})",
                "mask-image": f"var(--md-admonition-icon--{name})",
            },
        )

    def set_primary_foreground_color(
        self,
        color: datatypes.ColorType,
        light_shade: datatypes.ColorType | None = None,
        dark_shade: datatypes.ColorType | None = None,
    ):
        if light_shade is None:
            light_shade = color
        if dark_shade is None:
            dark_shade = color
        color_str = get_color_str(color)
        self[self.PREFIX]["--md-primary-fg-color"] = color_str
        self[self.PREFIX]["--md-primary-fg-color--light"] = get_color_str(light_shade)
        self[self.PREFIX]["--md-primary-fg-color--dark"] = get_color_str(dark_shade)
        return color_str

    def set_primary_background_color(
        self,
        color: datatypes.RGBColorType,
    ):
        color_str = get_color_str(color)
        self[self.PREFIX]["--md-primary-bg-color"] = color_str
        self[self.PREFIX]["--md-primary-bg-color--light"] = color_str
        return color_str

    def set_accent_foreground_color(
        self,
        color: datatypes.RGBColorType,
    ):
        color_str = get_color_str(color)
        self[self.PREFIX]["--md-accent-fg-color"] = color_str
        self[self.PREFIX]["--md-accent-fg-color--transparent"] = color_str
        return color_str

    def set_default_icon(self, icon_type: IconTypeStr, data: str):
        typ = ICON_TYPE[icon_type]
        self[self.PREFIX][f"--{typ}"] = wrap_svg(data)

    def add_status_icon(self, name: str, data: str):
        self[self.PREFIX][f"--md-status--{name}"] = wrap_svg(data)
        self.add_rule(
            f".md-status--{name}:after",
            {
                "-webkit-mask-image": f"var(--md-status--{name})",
                "mask-image": f"var(--md-status--{name})",
            },
        )

    def show_annotation_numbers(self):
        self.add_rule(
            ".md-typeset .md-annotation__index > ::before",
            {"content": "attr(data-md-annotation-id)"},
        )
        self.add_rule(
            ".md-typeset :focus-within > .md-annotation__index > ::before",
            {"transform": "none"},
        )


if __name__ == "__main__":
    ss = RootCSS()
    ss.set_primary_background_color((100, 100, 100))
    print(ss)
