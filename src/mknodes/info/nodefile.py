from __future__ import annotations

import functools
from typing import TYPE_CHECKING, Any

from jinjarope import inspectfilters, textfilters
from pydantic import BaseModel

from mknodes.info import configfile
from mknodes.utils import resources


if TYPE_CHECKING:
    from collections.abc import AsyncIterator
    import os
    import pathlib

    import mknodes as mk


class Example(BaseModel, extra="forbid"):
    """Model for a single example definition."""

    title: str | None = None
    jinja: str | None = None
    python: str | None = None
    description: str | None = None
    condition: str | None = None


class Output(BaseModel, extra="forbid"):
    """Model for a single output definition."""

    template: str


@functools.cache
def get_nodefile(klass: type) -> NodeFile | None:
    if file := find_file(klass):
        nodefile = NodeFile(file)
        if nodefile.name == klass.__name__:
            return nodefile
    return None


def find_file(klass: type) -> pathlib.Path | None:
    path = inspectfilters.get_file(klass)
    assert path
    if (file := path.parent / f"{klass.__name__}.toml").exists():
        return file
    if (file := path.parent / f"{klass.__name__}.toml".lower()).exists():
        return file
    if (file := path.parent / "metadata.toml").exists():
        return file
    return None


async def get_representations(jinja: str, parent: mk.MkNode) -> dict[str, str | mk.MkNode]:
    import mknodes as mk

    await parent.env.render_string_async(jinja)
    nodes = parent.env.rendered_nodes
    node = mk.MkContainer(nodes) if len(nodes) > 1 else nodes[0]
    dct: dict[str, str | mk.MkNode] = dict(
        Jinja=mk.MkCode(jinja, language="jinja"),
        Repr=mk.MkCode(textfilters.format_code(repr(node))),
        Rendered=node.__copy__(),
        Markdown=mk.MkCode(node, language="markdown"),
        Html=mk.MkCode(await node.to_html(), language="html"),
    )
    nodefile = node.get_nodefile()
    assert nodefile
    if "rst" in nodefile.output:
        output = await node.env.render_template_async("output/rst/template")
        dct["reST"] = mk.MkCode(output, language="rst")
    if "github" in nodefile.output:
        output = await node.env.render_template_async("output/github/template")
        dct["GitHub"] = mk.MkCode(output, language="markdown")
    if len(node.get_children()) > 0:
        dct["Repr tree"] = mk.MkTreeView(node)
    return dct


class NodeFile(configfile.TomlFile):
    def __init__(self, path_or_cls: str | os.PathLike[str] | type) -> None:
        path = find_file(path_or_cls) if isinstance(path_or_cls, type) else path_or_cls
        super().__init__(path)

    @property
    def icon(self) -> str:
        """Return the icon from metadata."""
        return self._data["metadata"]["icon"]

    @property
    def status(self) -> str:
        """Return the status from metadata."""
        return self._data["metadata"].get("status")

    @property
    def name(self) -> str:
        """Return the name from metadata."""
        return self._data["metadata"].get("name")

    @property
    def group(self) -> str:
        """Return the group from metadata."""
        return self._data["metadata"].get("group")

    @property
    def examples(self) -> dict[str, Example]:
        """Return the examples section."""
        return {k: Example.model_validate(v) for k, v in self._data.get("examples", {}).items()}

    async def get_examples(self, parent: mk.MkNode) -> dict[str, dict[str, Any]]:
        """Return a dictionary containing examples.

        Contains example-name->dict-with-representations key-value pairs.
        Representations are Markdown, Html, Repr tree, jinja, rendered

        Args:
            parent: Parent for the created MkNodes
                    (most representations are wrapped in MkCode nodes)

        Examples:
            ```
            {"Example 1": {"Html": ..., "Markdown": ...}, ...}
            ```
        """
        examples = {}
        for example in self.examples.values():
            if example.condition and not await parent.env.render_condition_async(example.condition):
                continue
            if example.jinja:
                examples[example.title or "Default"] = await get_representations(
                    example.jinja, parent
                )
        return examples

    async def iter_example_instances(self, parent: mk.MkNode) -> AsyncIterator[mk.MkNode]:
        for example in self.examples.values():
            if example.jinja:
                await parent.env.render_string_async(example.jinja)
                for child in parent.env.rendered_children:
                    yield child

    @property
    def output(self) -> dict[str, Output]:
        """Return the `output` section of the file."""
        return {k: Output.model_validate(v) for k, v in self._data.get("output", {}).items()}

    @property
    def layouts(self) -> dict[str, str]:
        """Return the `layouts` section of the file."""
        return self._data.get("layouts", {})

    @property
    def requirements(self) -> dict[str, Any]:
        """Return the `requirements` section of the file."""
        return self._data.get("requirements", {})

    @property
    def extensions(self) -> list[resources.Extension]:
        """Return the required extensions defined in the file."""
        extensions = self.requirements.get("extension", {})
        return [resources.Extension(k, **v) for k, v in extensions.items()]

    @property
    def packages(self) -> list[resources.Package]:
        """Return the required packages defined in the file."""
        packages = self.requirements.get("package", {})
        return [resources.Package(k, **v) for k, v in packages.items()]

    @property
    def css(self) -> list[resources.CSSFile]:
        """Return the CSS resources defined in the file."""
        css: list[resources.CSSFile] = []
        res = self._data.get("resources", {})
        for item in res.get("css", []):
            if "filename" in item:
                instance = resources.CSSFile(item["filename"])
                css.append(instance)
        return css

    @property
    def js(self) -> list[resources.JSFile | resources.JSText]:
        """Return the JavaScript resources defined in the file."""
        js: list[resources.JSFile | resources.JSText] = []
        res = self._data.get("resources", {})
        for item in res.get("js", []):
            if "link" in item:
                file_instance = resources.JSFile(**item)
                js.append(file_instance)
            elif "content" in item:
                text_instance = resources.JSText(**item)
                js.append(text_instance)
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
