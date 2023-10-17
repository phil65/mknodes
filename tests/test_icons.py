from __future__ import annotations

from mknodes.utils import icons


def test_material_key_conversion():
    assert icons.get_pyconify_key("file") == "mdi:file"
    assert icons.get_pyconify_key("mdi:file") == "mdi:file"
    assert icons.get_pyconify_key("material/file") == "mdi:file"
    assert icons.get_pyconify_key(":material-file:") == "mdi:file"


def test_noto_key_conversion():
    assert icons.get_pyconify_key("noto:wrench") == "noto:wrench"
    assert icons.get_pyconify_key(":noto-wrench:") == "noto:wrench"
    assert icons.get_pyconify_key("simple/shieldsdotio") == "simple-icons:shieldsdotio"
    assert (
        icons.get_pyconify_key(":fontawesome-regular-keyboard:") == "fa6-regular:keyboard"
    )
    assert (
        icons.get_pyconify_key("fontawesome/regular/keyboard") == "fa6-regular:keyboard"
    )
