from __future__ import annotations

import markdownizer


def test_docstrings():
    docstrings = markdownizer.DocStrings(obj=markdownizer)
    assert str(docstrings) == "::: markdownizer\n\n"
