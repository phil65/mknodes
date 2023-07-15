from __future__ import annotations

import logging
import pathlib

import mkdocs_gen_files

from markdownizer import nav, utils


logger = logging.getLogger(__name__)


class Docs(nav.Nav):
    def __init__(self):
        super().__init__(section=None)
        self._editor = mkdocs_gen_files.editor.FilesEditor.current()
        self._docs_dir = pathlib.Path(self._editor.config["docs_dir"])
        self.files = self._editor.files

    def __repr__(self):
        return utils.get_repr(self, path=str(self._docs_dir))


if __name__ == "__main__":
    docs = Docs()
    subnav = docs.create_nav("subnav")
    page = subnav.create_page("My first page!")
    page.add_admonition("Warning This is still beta", typ="danger", title="Warning!")
    page2 = subnav.create_page("And a second one")
    subsubnav = subnav.create_nav("SubSubNav")
    subsubnav = subsubnav.create_page("SubSubPage")
    from pprint import pprint

    pprint(docs.all_virtual_files())
