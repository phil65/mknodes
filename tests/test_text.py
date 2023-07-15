import pytest

import markdownizer


def test_text():
    nav = markdownizer.Text()
    assert not str(nav)
