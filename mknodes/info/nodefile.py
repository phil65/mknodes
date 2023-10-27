from __future__ import annotations

import os

from mknodes.info import tomlfile
from mknodes.utils import resources


# from mknodes.utils import resources


class NodeFile(tomlfile.TomlFile):
    def __init__(self, path_or_cls: str | os.PathLike | type):
        from mknodes.utils import inspecthelpers

        if isinstance(path_or_cls, type):
            path = inspecthelpers.get_file(path_or_cls)  # type: ignore[arg-type]
            assert path
            path = path.parent / "metadata.toml"
        else:
            path = path_or_cls
        # text = pathhelpers.load_file_cached(path.parent / "metadata.toml")
        super().__init__(path)

    @property
    def icon(self) -> str:
        return self._data["metadata"]["icon"]

    @property
    def status(self) -> str:
        return self._data["metadata"].get("status")

    @property
    def name(self) -> str:
        return self._data["metadata"].get("name")

    @property
    def examples(self) -> dict[str, str]:
        return self._data.get("examples", {})

    @property
    def output(self) -> dict[str, str]:
        return self._data.get("output", {})

    @property
    def requirements(self):
        return self._data.get("requirements", {})

    @property
    def extensions(self):
        extensions = self.requirements.get("extension", {})
        return [resources.Extension(k, **v) for k, v in extensions.items()]

    # @property
    # def resources(self) -> resources.Resources:
    #     """Return the resources specific for this node."""
    #     extension = {k.extension_name: dict(k) for k in self.REQUIRED_EXTENSIONS}
    #     mod_resources = self.mods.get_resources()
    #     css_resources: list[resources.CSSType] = []
    #     for css in self.CSS + mod_resources.css:
    #         if isinstance(css, resources.CSSFile) and css.is_local():
    #             text = self.env.render_template(css.link)
    #             css_resource = resources.CSSText(text, css.link)
    #             css_resources.append(css_resource)
    #         else:
    #             css_resources.append(css)
    #     js_resources: list[resources.JSType] = []
    #     for js_file in self.JS_FILES + mod_resources.js:
    #         if isinstance(js_file, resources.JSFile) and js_file.is_local():
    #             text = self.env.render_template(js_file.link)
    #             js_resource = resources.JSText(
    #                 text,
    #                 js_file.link,
    #                 defer=js_file.defer,
    #                 async_=js_file.async_,
    #                 crossorigin=js_file.crossorigin,
    #                 typ=js_file.typ,
    #                 is_library=js_file.is_library,
    #             )
    #             js_resources.append(js_resource)
    #         else:
    #             js_resources.append(js_file)
    #     return resources.Resources(
    #         js=js_resources,
    #         markdown_extensions=extension,
    #         plugins=self.REQUIRED_PLUGINS,
    #         css=css_resources,
    #     )


if __name__ == "__main__":
    import mknodes as mk

    info = NodeFile(mk.MkCode)
    print(info.extensions)
