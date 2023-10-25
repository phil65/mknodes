from __future__ import annotations

import mknodes as mk


EXPECTED_IN_ANNOTATIONS = """\
1.  ::: mknodes.basenodes._mkdocstrings.MkDocStrings.__init__
        options:
          docstring_section_style: 'list'
          show_root_heading: True
    \n"""


def test_docstrings():
    docstrings = mk.MkDocStrings(obj=mk)
    assert str(docstrings) == "::: mknodes\n"


def test_auto_list_style_inside_annotations():
    annotations = mk.MkAnnotations()
    annotations[1] = mk.MkDocStrings(obj=mk.MkDocStrings.__init__)
    assert str(annotations) == EXPECTED_IN_ANNOTATIONS
