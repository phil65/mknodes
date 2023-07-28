from __future__ import annotations

from mknodes.utils import inventorymanager


DOTTED_PATH = "prettyqt.widgets.widget.WidgetMixin.set_style"
BASE_URL = "http://test.de"
EXPECTED = f"http://test.de/qt_modules/widgets/WidgetMixin.html#{DOTTED_PATH}"


def test_getting_link(test_data_dir):
    inv_manager = inventorymanager.InventoryManager()
    inv_manager.add_inv_file(test_data_dir / "objects.inv", base_url=BASE_URL)
    item = inv_manager[DOTTED_PATH]
    assert item == EXPECTED
