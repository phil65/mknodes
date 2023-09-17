from __future__ import annotations

import collections
import os
import pathlib

import markdown

from mkdocs.config.defaults import MkDocsConfig
from mkdocs.plugins import get_plugin_logger
from mkdocs.structure import files as files_

from mknodes import mkdocsconfig
from mknodes.pages import pagetemplate
from mknodes.plugin import buildbackend, mkdocsbuilder, mkdocshelpers
from mknodes.utils import mergehelpers, pathhelpers, requirements


logger = get_plugin_logger(__name__)


class MkDocsBackend(buildbackend.BuildBackend):
    def __init__(
        self,
        files: files_.Files | None = None,
        config: mkdocsconfig.Config | MkDocsConfig | str | os.PathLike | None = None,
        directory: str | os.PathLike | None = None,
    ):
        match config:
            case mkdocsconfig.Config():
                self._config = config._config
            case MkDocsConfig():
                self._config = config
            case _:
                self._config = mkdocsconfig.Config(config)._config
        super().__init__(directory)
        files_map = {pathlib.PurePath(f.src_path).as_posix(): f for f in files or []}
        self._mk_files: collections.ChainMap[str, files_.File] = collections.ChainMap(
            {},
            files_map,
        )
        self.builder = mkdocsbuilder.MkDocsBuilder(self._config)

    def _get_parser(self) -> markdown.Markdown:
        """Return a markdown instance based on given config."""
        return markdown.Markdown(
            extensions=self._config.markdown_extensions,
            extension_configs=self._config.mdx_configs,
        )

    @property
    def files(self) -> files_.Files:
        """Access the files as they currently are, as a MkDocs [Files][] collection.

        [Files]: https://github.com/mkdocs/mkdocs/blob/master/mkdocs/structure/files.py
        """
        files = sorted(self._mk_files.values(), key=mkdocshelpers.file_sorter)
        return files_.Files(files)

    def on_collect(self, files: dict[str, str | bytes], reqs: requirements.Requirements):
        logger.info("Finished writing pages to disk")
        self.write_files(files)
        logger.info("Finished writing pages to disk")
        logger.info("Adding requirements to Config and build...")
        for k, v in reqs.css.items():
            self.add_css_file(k, v)
        for k, v in reqs.js_files.items():
            self.add_js_file(k, v)
        if extensions := reqs.markdown_extensions:
            self.register_extensions(extensions)
        for template in reqs.templates:
            self.add_template(template)

    def _write_file(self, path: str | os.PathLike, content: str | bytes):
        path = pathlib.PurePath(path).as_posix()
        file_for_path = self.builder.get_file(path, src_dir=self.directory)
        new_path = pathlib.Path(file_for_path.abs_src_path)
        target_path = None
        if path not in self._mk_files:
            new_path.parent.mkdir(exist_ok=True, parents=True)
            self._mk_files[path] = file_for_path
            target_path = new_path

        f = self._mk_files[path]
        source_path = pathlib.Path(f.abs_src_path)
        if source_path != new_path:
            self._mk_files[path] = file_for_path
            pathhelpers.copy(source_path, new_path)
            target_path = new_path
        pathhelpers.write_file(content, target_path or source_path)

    def register_extensions(self, extensions: dict[str, dict]):
        for ext_name in extensions:
            if ext_name not in self._config.markdown_extensions:
                logger.info("Adding %s to extensions", ext_name)
                self._config.markdown_extensions.append(ext_name)
        self._config.mdx_configs = mergehelpers.merge_dicts(
            self._config.mdx_configs,
            extensions,
        )

    def add_css_file(self, filename: str | os.PathLike, css: str):
        """Register a css file.

        Writes file to build assets folder and registers extra_css in config

        Arguments:
            filename: Filename to write
            css: file content
        """
        path = (pathlib.Path("assets") / filename).as_posix()
        self._config.extra_css.append(path)
        abs_path = pathlib.Path(self._config.site_dir) / path
        logger.info("Registering css file %s...", abs_path)
        pathhelpers.write_file(css, abs_path)

    def add_js_file(self, filename: str | os.PathLike, js: str):
        """Register a javascript file.

        Writes file to build assets folder and registers extra_javascript in config

        Arguments:
            filename: Filename to write
            js: file content
        """
        path = (pathlib.Path("assets") / filename).as_posix()
        self._config.extra_javascript.append(path)
        abs_path = pathlib.Path(self._config.site_dir) / path
        logger.info("Registering js file %s...", abs_path)
        pathhelpers.write_file(js, abs_path)

    def add_template(self, template: pagetemplate.PageTemplate):
        """Register a html template.

        Writes file to build custom_dir folder

        Arguments:
            template: Template object
        """
        if not self._config.theme.custom_dir:
            logger.warning("Cannot write template. No custom_dir set in config.")
            return
        md = self._get_parser()
        if html := template.build_html(md):
            target_path = pathlib.Path(self._config.theme.custom_dir) / template.filename
            # path = pathlib.Path("overrides") / filename
            logger.info("Creating %s...", target_path.as_posix())
            pathhelpers.write_file(html, target_path)


if __name__ == "__main__":
    backend = MkDocsBackend()

    from mknodes import paths, project
    from mknodes.theme import theme as theme_

    skin = theme_.Theme("material")
    proj = project.Project(
        base_url="",
        use_directory_urls=True,
        theme=skin,
        repo=".",
        build_fn=paths.DEFAULT_BUILD_FN,
        clone_depth=1,
    )
    proj.build()
    reqs = proj.get_requirements()
