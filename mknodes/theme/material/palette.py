from __future__ import annotations

import dataclasses

from xml.etree import ElementTree

from mknodes.utils import xmlhelpers


SCRIPT = """
  var palette = __md_get("__palette")
  if (palette && typeof palette.color === "object")
    for (var key of Object.keys(palette.color))
      document.body.setAttribute("data-md-color-" + key, palette.color[key])
"""


@dataclasses.dataclass
class Palette:
    """Class representing a MkDocs-Material palette."""

    scheme: str = "default"
    primary: str = "indigo"
    accent: str = "indigo"
    media: str | None = None
    toggle_name: str | None = None
    toggle_icon: str | None = None


def build_toggle(palettes: list[Palette]) -> ElementTree.Element:
    """Builds the XML equivalent to the content of "palette.html" partial."""
    # body = ElementTree.Element("body")
    # form = ElementTree.SubElement(
    # body,
    form = ElementTree.Element(
        "form",
        {"class": "md-header__option", "data-md-component": "palette"},
    )
    for i, pal in enumerate(palettes):
        mode = "dark" if pal.scheme == "slate" else "light"
        attrs = {
            "class": "md-option",
            "data-md-color-media": f"(prefers-color-scheme: {mode})",
            "data-md-color-scheme": pal.scheme.replace(" ", "-"),
            "data-md-color-primary": pal.primary.replace(" ", "-"),
            "data-md-color-accent": pal.accent.replace(" ", "-"),
            "type": "radio",
            "name": "__palette",
            "id": f"__palette_{i + 1}",
        }
        if pal.toggle_name:
            attrs["aria-label"] = pal.toggle_name
        else:
            attrs["aria-hidden"] = "true"
        el_input = ElementTree.SubElement(form, "input", attrs)
        if pal.toggle_name:
            attrs = {
                "class": "md-header__button md-icon",
                "title": pal.toggle_name,
                "for": f"__palette_{i or len(palettes)}",
                "hidden": "hidden",
            }
            label = ElementTree.SubElement(el_input, "label", attrs)
            el = xmlhelpers.get_material_icon_svg(
                pal.toggle_icon or "material/brightness-4",
            )
            label.append(el)
    # script = ElementTree.SubElement(body, "script")
    # script.text = SCRIPT
    return form


if __name__ == "__main__":
    default_palette = Palette()
    dark_palette = Palette(
        toggle_name="Switch to light mode",
        toggle_icon="material/brightness-4",
        scheme="slate",
    )
    root = build_toggle([default_palette, dark_palette])
    xml_string = xmlhelpers.pformat(root)
    print(xml_string)
