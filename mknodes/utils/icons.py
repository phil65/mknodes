from __future__ import annotations

import functools
from typing import TYPE_CHECKING, Any
import xml.etree.ElementTree as ET

from jinjarope import iconfilters, icons


if TYPE_CHECKING:
    from collections.abc import Sequence

    import markdown


def icon_for_url(url: str) -> str | None:
    """Return a pyconify icon key for given url."""
    from urllib import parse

    socials = {
        "matrix.to": "fa-brands:gitter",
        "x.com": "fa-brands:twitter",
        "fosstodon.org": "fa-brands:mastodon",
    }
    netloc = parse.urlsplit(url).netloc.lower()

    # First check exact matches
    if icon := socials.get(netloc):
        return icon

    # Try to find a matching brand icon
    domain = netloc.split(".")[-2]
    icon_index = icons._get_pyconify_icon_index()
    if (icon_name := f":fa-brands-{domain}:") in icon_index:
        return iconfilters.get_pyconify_key(icon_index[icon_name]["name"])

    return None


@functools.cache
def _patch_index_with_sets(icon_sets: Sequence[str]) -> dict[str, Any]:
    from pymdownx import twemoji_db

    # Copy the Twemoji index
    index = {
        "name": "twemoji",
        "emoji": twemoji_db.emoji,
        "aliases": twemoji_db.aliases,
    }
    # icon_index = _get_pyconify_icon_index(*icon_sets)
    icon_index = icons.load_icon_index()
    index["emoji"].update(icon_index)
    return index


def twemoji(options: dict[str, Any], md: markdown.Markdown) -> dict[str, Any]:
    """Provide a copied Twemoji index with additional codes for Pyconify icons.

    Used for pymdownx.emoji.
    """
    default = list(icons.PYCONIFY_TO_PREFIXES.keys())
    icon_sets = options.get("icon_sets", default)[:]
    return _patch_index_with_sets(tuple(icon_sets))


def to_svg(
    index: str,
    shortname: str,
    alias: str,
    uc: str | None,
    alt: str,
    title: str,
    category: str,
    options: dict[str, str],
    md: markdown.Markdown,
):
    """Return svg element (wrapped in a span element).

    Used for pymdownx.emoji.
    """
    from pymdownx.emoji import TWEMOJI_SVG_CDN, add_attributes

    is_unicode = uc is not None
    if is_unicode:
        image_path = options.get("image_path", TWEMOJI_SVG_CDN)
        attributes = {
            "class": options.get("classes", index),
            "alt": alt,
            "src": f"{image_path}{uc}.svg",
        }

        if title:
            attributes["title"] = title

        add_attributes(options, attributes)

        return ET.Element("img", attributes)
    el = ET.Element("span", {"class": options.get("classes", index)})
    svg_path = md.inlinePatterns["emoji"].emoji_index["emoji"][shortname]["path"]  # type: ignore[attr-defined]
    svg = iconfilters.get_icon_svg(svg_path)
    el.text = md.htmlStash.store(svg)
    return el


def get_emoji_slug(icon: str) -> str:
    """Return a icon string which can be used in markdown texts.

    The icon string will get picked up by pymdownx.emoji extension.

    Args:
        icon: The string to convert to an emoji slug.
    """
    return f":{iconfilters.get_pyconify_key(icon).replace(':', '-')}:"


def get_icon_xml(icon: str) -> ET.Element:
    """Return a xmlElement for given MaterialIcon.

    Args:
        icon: Icon to fetch. If iconname is not explicit (aka does not contain "/"),
              then it will try to get the icon from material/ folder.
    """
    ET.register_namespace("", "http://www.w3.org/2000/svg")
    svg_text = iconfilters.get_icon_svg(icon)
    return ET.fromstring(svg_text)
