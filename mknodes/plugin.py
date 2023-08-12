from __future__ import annotations

# Taken from mkdocs-gen-files
import logging
import pathlib
import tempfile
import urllib.parse

from mkdocs.config import Config
from mkdocs.plugins import BasePlugin
from mkdocs.structure.files import Files
from mkdocs.structure.pages import Page


try:
    from mkdocs.exceptions import PluginError
except ImportError:
    PluginError = SystemExit  # type: ignore

from mkdocs_gen_files.config_items import ListOfFiles
from mkdocs_gen_files.editor import FilesEditor


try:
    from mkdocs.plugins import event_priority
except ImportError:

    def event_priority(priority):
        return lambda f: f  # No-op fallback


log = logging.getLogger(f"mkdocs.plugins.{__name__}")


class MkNodesPlugin(BasePlugin):
    config_scheme = (("scripts", ListOfFiles(required=True)),)

    def on_files(self, files: Files, config: Config) -> Files:
        self._dir = tempfile.TemporaryDirectory(prefix="mknodes_")

        with FilesEditor(files, config, self._dir.name) as ed:
            for file_name in self.config["scripts"]:
                try:
                    import importlib.util
                    import sys

                    file_path = file_name
                    module_name = pathlib.Path(file_name).stem
                    spec = importlib.util.spec_from_file_location(module_name, file_path)
                    if spec is None:
                        raise RuntimeError
                    module = importlib.util.module_from_spec(spec)
                    sys.modules[module_name] = module
                    spec.loader.exec_module(module)  # type: ignore[union-attr]
                    module.build(config, files)
                except SystemExit as e:
                    if e.code:
                        msg = f"Script {file_name!r} caused {e!r}"
                        raise PluginError(msg) from e

        self._edit_paths = dict(ed.edit_paths)
        return ed.files

    def on_page_content(self, html, page: Page, config: Config, files: Files):
        repo_url = config.get("repo_url", None)
        edit_uri = config.get("edit_uri", None)

        src_path = pathlib.PurePath(page.file.src_path).as_posix()
        if src_path in self._edit_paths:
            path = self._edit_paths.pop(src_path)
            if repo_url and edit_uri:
                # Ensure urljoin behavior is correct
                if not edit_uri.startswith(("?", "#")) and not repo_url.endswith("/"):
                    repo_url += "/"

                page.edit_url = path and urllib.parse.urljoin(
                    urllib.parse.urljoin(repo_url, edit_uri),
                    path,
                )

        return html

    @event_priority(-100)
    def on_post_build(self, config: Config):
        self._dir.cleanup()

        if unused_edit_paths := {k: str(v) for k, v in self._edit_paths.items() if v}:
            msg = "mkdocs_gen_files: These set_edit_path invocations went unused: %r"
            log.warning(msg, unused_edit_paths)
