from __future__ import annotations

import mknodes


EXPECTED_IN_ANNOTATIONS = """1.  ::: mknodes.basenodes._mkdocstrings.MkDocStrings.__init__
        options:
          docstring_section_style: 'list'
          show_root_heading: True
    """ + "\n"  # noqa: ISC003


def test_docstrings():
    docstrings = mknodes.MkDocStrings(obj=mknodes)
    assert str(docstrings) == "::: mknodes\n"


def test_auto_list_style_inside_annotations():
    annotations = mknodes.MkAnnotations()
    annotations[1] = mknodes.MkDocStrings(obj=mknodes.MkDocStrings.__init__)
    assert str(annotations) == EXPECTED_IN_ANNOTATIONS
