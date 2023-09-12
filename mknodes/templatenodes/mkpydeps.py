from __future__ import annotations

from collections.abc import Mapping
import functools
import os
import types

from typing import Any

from mknodes.basenodes import mknode
from mknodes.utils import inspecthelpers, log, reprhelpers


logger = log.get_logger(__name__)


@functools.cache
def get_dependency_svg(
    folder_name: str | os.PathLike,
    max_bacon: int | None = 2,
    max_module_depth: int | None = None,
    only_cycles: bool = False,
    clusters: bool = False,
) -> str:
    """Get svg for given folder (like "src/module" or just "module")."""
    from pydeps import cli, colors, dot, py2depgraph
    from pydeps.pydeps import depgraph_to_dotsrc
    from pydeps.target import Target

    cli.verbose = cli._not_verbose
    cmd = [str(folder_name), "--noshow"]
    if max_bacon:
        cmd.extend(["--max-bacon", str(max_bacon)])
    if max_module_depth:
        cmd.extend(["--max-module-depth", str(max_module_depth)])
    if only_cycles:
        cmd.append("--only-cycles")
    if clusters:
        cmd.append("--clusters")
    options = cli.parse_args(cmd)
    colors.START_COLOR = options["start_color"]
    target = Target(options["fname"])
    logger.debug("run py2dep for folder %r", str(folder_name))
    with target.chdir_work():
        dep_graph = py2depgraph.py2dep(target, **options)
    logger.debug("run depgraph_to_dotsrc")
    dot_src = depgraph_to_dotsrc(target, dep_graph, **options)
    logger.debug("run call_graphviz_dot")
    svg = dot.call_graphviz_dot(dot_src, "svg").decode()
    svg = "".join(svg.splitlines()[6:])
    return svg.replace('fill="white"', 'fill="transparent"')


def insert_links(svg: str, link_map: Mapping[str, str]):
    for k, v in link_map.items():
        if (title_tag := f'<title>{k.replace(".", "_")}</title>') in svg:
            svg = svg.replace(title_tag, f'<a href="{v}"><title>{k}</title>')
    return svg.replace("</text></g>", "</text></a></g>")


class MkPyDeps(mknode.MkNode):
    """Node for showing a Dependency graph."""

    ICON = "material/code-json"

    def __init__(
        self,
        module: str | os.PathLike | types.ModuleType | None = None,
        max_bacon: int | None = None,
        max_module_depth: int | None = None,
        only_cycles: bool = False,
        clusters: bool = False,
        **kwargs: Any,
    ):
        """Constructor.

        Arguments:
            module: Path to the module
            max_bacon: Max bacon
            max_module_depth: Maximum module depth to display
            only_cycles: Only show import cycles
            clusters: draw external dependencies as separate clusters
            kwargs: Keyword arguments passed to parent
        """
        self._module = module
        self.max_bacon = max_bacon
        self.max_module_depth = max_module_depth
        self.only_cycles = only_cycles
        self.clusters = clusters
        super().__init__(**kwargs)

    def __repr__(self):
        return reprhelpers.get_repr(
            self,
            module=self.module,
            max_bacon=self.max_bacon,
            max_module_depth=self.max_module_depth,
            only_cycles=self.only_cycles,
            clusters=self.clusters,
            _filter_empty=True,
            _filter_false=True,
        )

    @property
    def module(self):
        match self._module:
            case str() | os.PathLike:
                return self._module
            case types.ModuleType():
                return inspecthelpers.get_file(self._module)
            case _:
                return self.ctx.metadata.distribution_name

    def _to_markdown(self) -> str:
        content = get_dependency_svg(
            self.module,
            max_bacon=self.max_bacon,
            max_module_depth=self.max_module_depth,
            only_cycles=self.only_cycles,
            clusters=self.clusters,
        )
        content = insert_links(content, self.ctx.links.inv_manager)
        return f"<body>\n\n{content}\n\n</body>\n"

    @staticmethod
    def create_example_page(page):
        import mknodes

        node = MkPyDeps("mknodes/data/tools.py", max_bacon=1, max_module_depth=1)
        page += mknodes.MkReprRawRendered(node)


if __name__ == "__main__":
    node = MkPyDeps.with_default_context("mknodes/data/tools.py", max_bacon=1)
    print(node)
