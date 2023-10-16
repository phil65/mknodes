from __future__ import annotations

from collections.abc import Sequence
import functools
import inspect
import pathlib

from typing import Any
import xml.etree.ElementTree as etree

import material

from pymdownx.emoji import TWEMOJI_SVG_CDN, add_attributes


RESOURCES = pathlib.Path(inspect.getfile(material)).parent
RES_PATH = RESOURCES / "templates" / ".icons"


PYCONIFY_TO_PREFIXES = {
    "mdi": "material",
    "simple-icons": "simple",
    "octicon": "octicons",
    "fa-regular": "fontawesome-regular",
    "fa-brands": "fontawesome-brands",
    "fa-solid": "fontawesome-solid",
}


def get_collection_map(*prefixes):
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


def get_pyconify_icon_index(*collections) -> dict[str, dict[str, str]]:
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
def _patch_index_for_locations(icon_locations: Sequence[str]) -> dict[str, Any]:
    from pymdownx import twemoji_db

    # Copy the Twemoji index
    index = {
        "name": "twemoji",
        "emoji": twemoji_db.emoji,
        "aliases": twemoji_db.aliases,
    }
    icons = get_pyconify_icon_index("mdi")
    index["emoji"].update(icons)
    return index


def twemoji(options: dict[str, Any], md):
    """Provide a copied Twemoji index with additional codes for Pyconify icons."""
    icon_locations = options.get("custom_icons", [])[:]
    icon_locations.append(str(RES_PATH))
    return _patch_index_for_locations(tuple(icon_locations))


def to_svg(index, shortname, alias, uc, alt, title, category, options, md):
    """Return SVG element."""
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


def get_material_icon_path(icon: str) -> pathlib.Path:
    import material

    if "/" not in icon:
        icon = f"material/{icon}"
    path = next(iter(material.__path__))
    return pathlib.Path(path) / "templates" / ".icons" / f"{icon}.svg"


def get_icon_svg(icon: str) -> str:
    if icon.startswith(":") or ":" not in icon:
        path = get_material_icon_path(icon)
        return path.read_text()
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


if __name__ == "__main__":
    idx = get_collection_map("mdi")
    print(idx)
