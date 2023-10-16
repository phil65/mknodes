from __future__ import annotations

from collections.abc import Sequence
import functools

from typing import Any
import xml.etree.ElementTree as etree


PYCONIFY_TO_PREFIXES = {
    "mdi": "material",
    "simple-icons": "simple",
    "octicon": "octicons",
    "fa-regular": "fontawesome-regular",
    "fa-brands": "fontawesome-brands",
    "fa-solid": "fontawesome-solid",
}


def get_collection_map(*prefixes: str) -> dict[str, list[str]]:
    """Return a dictionary with a mapping from pyconify name to icon prefixes.

    In order to provide compatibility with the materialx-icon-index,
    we also add the prefixes used by that index, which is different from
    the pyconify prefixes. (material vs mdi etc, see PYCONIFY_TO_PREFIXES)
    """
    import pyconify

    mapping = {coll: [coll] for coll in pyconify.collections(*prefixes)}
    for k, v in PYCONIFY_TO_PREFIXES.items():
        if k in mapping:
            mapping[k].append(v)
    return mapping


def get_pyconify_icon_index(*collections: str) -> dict[str, dict[str, str]]:
    """Return a icon index for the pymdownx emoji extension containing pyconify icons.

    The dictionaries contain two key-value pairs:
    "name" is the emoji identifier,
    "path" is the pyconify key

    """
    import pyconify

    index = {}
    for coll, prefixes in get_collection_map(*collections).items():
        collection = pyconify.collection(coll)
        for icon_name in collection.get("uncategorized", []):
            for prefix in prefixes:
                name = f":{prefix}-{icon_name}:"
                index[name] = {"name": name, "path": f"{coll}:{icon_name}"}
        for cat in pyconify.collection(coll).get("categories", {}).values():
            for icon_name in cat:
                for prefix in prefixes:
                    name = f":{prefix}-{icon_name}:"
                    index[name] = {"name": name, "path": f"{coll}:{icon_name}"}
    return index


@functools.cache
def _patch_index_for_locations(icon_sets: Sequence[str]) -> dict[str, Any]:
    from pymdownx import twemoji_db

    # Copy the Twemoji index
    index = {
        "name": "twemoji",
        "emoji": twemoji_db.emoji,
        "aliases": twemoji_db.aliases,
    }
    icons = get_pyconify_icon_index(*icon_sets)
    index["emoji"].update(icons)
    return index


def twemoji(options: dict[str, Any], md):
    """Provide a copied Twemoji index with additional codes for Pyconify icons."""
    default = list(PYCONIFY_TO_PREFIXES.keys())
    icon_sets = options.get("icon_sets", default)[:]
    return _patch_index_for_locations(tuple(icon_sets))


def to_svg(index, shortname, alias, uc, alt, title, category, options, md):
    """Return SVG element."""
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

        return etree.Element("img", attributes)
    el = etree.Element("span", {"class": options.get("classes", index)})
    svg_path = md.inlinePatterns["emoji"].emoji_index["emoji"][shortname]["path"]
    svg = get_icon_svg(svg_path)
    el.text = md.htmlStash.store(svg)
    return el


def get_icon_svg(icon: str) -> str:
    """Return svg for given pyconify icon key.

    Key should look like "mdi:file"
    For compatibility, this method also supports compatibility for
    emoji-slugs (":material-file:") as well as material-paths ("material/file")

    If no group is supplied, mdi is assumed as group:

    Example:
        get_icon_svg("file")  # implicit mdi group
        get_icon_svg("mdi:file")  # pyconify key
        get_icon_svg("material/file")  # Material-style path
        get_icon_svg(":material-file:")  # material-style emoji slug
    """
    for k, v in PYCONIFY_TO_PREFIXES.items():
        path = f'{v.replace("-", "/")}/'
        icon = icon.replace(path, f"{k}:")
        icon = icon.replace(f":{v}-", f"{k}:")

    icon = icon.strip(":")
    if ":" not in icon:
        icon = f"mdi:{icon}"
    import pyconify

    return pyconify.svg(icon).decode()


def get_icon_xml(icon: str) -> etree.Element:
    """Return a xmlElement for given MaterialIcon.

    Arguments:
        icon: Icon to fetch. If iconname is not explicit (aka does not contain "/"),
              then it will try to get the icon from material/ folder.
    """
    etree.register_namespace("", "http://www.w3.org/2000/svg")
    svg_text = get_icon_svg(icon)
    return etree.fromstring(svg_text)
