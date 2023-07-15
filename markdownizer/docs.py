from __future__ import annotations

import logging
import pathlib

import mkdocs_gen_files

from markdownizer import moduledocumentation, nav


logger = logging.getLogger(__name__)


class Docs(nav.Nav):
    def __init__(self):
        super().__init__(section=None)
        self._editor = mkdocs_gen_files.editor.FilesEditor.current()
        self._docs_dir = pathlib.Path(self._editor.config["docs_dir"])
        self.files = self._editor.files

    def create_documentation(self, module) -> moduledocumentation.ModuleDocumentation:
        nav = moduledocumentation.ModuleDocumentation(module=module, parent=self)
        self.nav[(nav.module_name,)] = f"{nav.module_name}/"
        self.navs.append(nav)
        return nav


if __name__ == "__main__":
    doc = Docs()
    page = doc.add_overview_page()
    print(page)
