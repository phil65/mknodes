from __future__ import annotations

import functools
import os
import pathlib

from mknodes.info import tomlfile
from mknodes.utils import resources


# from mknodes.utils import resources


@functools.cache
def get_nodefile(klass: type) -> NodeFile | None:
    file = find_file(klass)
    if file.exists():
        return NodeFile(file)
    return None


def find_file(klass: type) -> pathlib.Path:
    from mknodes.utils import inspecthelpers

    path = inspecthelpers.get_file(klass)  # type: ignore[arg-type]
    assert path
    # text = pathhelpers.load_file_cached(path.parent / "metadata.toml")
    return path.parent / "metadata.toml"


def get_representations(jinja: str, parent) -> dict[str, str | mk.MkNode]:
    import mknodes as mk

    parent.env.render_string(jinja)
    nodes = parent.env.rendered_nodes
    node = mk.MkContainer(nodes) if len(nodes) > 1 else nodes[0]
    dct: dict[str, str | mk.MkNode] = dict(  # type: ignore[annotation-unchecked]
        Jinja=mk.MkCode(jinja, language="jinja"),
        Repr=mk.MkCode(repr(node)),
        Rendered=node.__copy__(),
        Markdown=mk.MkCode(node, language="markdown"),
        Html=mk.MkCode(node.to_html(), language="html"),
    )
    if len(node.children) > 0:
        dct["Repr tree"] = mk.MkTreeView(node)
    return dct


class NodeFile(tomlfile.TomlFile):
    def __init__(self, path_or_cls: str | os.PathLike | type):
        path = find_file(path_or_cls) if isinstance(path_or_cls, type) else path_or_cls
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

    def get_examples(self, parent) -> dict[str, dict]:
        examples = {}
        for v in self._data.get("examples", {}).values():
            if "jinja" in v:
                examples[v["title"]] = get_representations(v["jinja"], parent)
        return examples

    @property
    def output(self) -> dict[str, str]:
        return self._data.get("output", {})

    @property
    def requirements(self):
        return self._data.get("requirements", {})

    @property
    def extensions(self) -> list[resources.Extension]:
        extensions = self.requirements.get("extension", {})
        return [resources.Extension(k, **v) for k, v in extensions.items()]

    @property
    def packages(self) -> list[resources.Package]:
        packages = self.requirements.get("package", {})
        return [resources.Package(k, **v) for k, v in packages.items()]

    @property
    def css(self) -> list[resources.CSSFile]:
        css: list[resources.CSSFile] = []
        res = self._data.get("resources", {})
        for item in res.get("css", []):
            if "filename" in item:
                instance = resources.CSSFile(item["filename"])
                css.append(instance)
        return css

    @property
    def js(self) -> list[resources.JSFile]:
        js: list[resources.JSFile] = []
        res = self._data.get("resources", {})
        for item in res.get("js", []):
            if "link" in item:
                item = item.copy()
                name = item.pop("link")
                instance = resources.JSFile(name, **item)
                js.append(instance)
        return js

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
