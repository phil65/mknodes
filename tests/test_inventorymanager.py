from __future__ import annotations

import pytest

from mknodes.utils import inventorymanager


DOTTED_PATH = "prettyqt.widgets.widget.WidgetMixin.set_style"
BASE_URL = "http://test.de"
EXPECTED = f"http://test.de/qt_modules/widgets/WidgetMixin.html#{DOTTED_PATH}"


def test_getting_link(test_data_dir):
    """Tests the functionality of getting a link from the inventory manager.
    
    Args:
        test_data_dir (pathlib.Path): The directory containing test data files.
    
    Returns:
        None: This method doesn't return anything explicitly.
    
    Raises:
        AssertionError: If the retrieved item doesn't match the expected value.
    """
    inv_manager = inventorymanager.InventoryManager()
    inv_manager.add_inv_file(test_data_dir / "objects.inv", base_url=BASE_URL)
    item = inv_manager[DOTTED_PATH]
    assert item == EXPECTED


if __name__ == "__main__":
    pytest.main([__file__])
