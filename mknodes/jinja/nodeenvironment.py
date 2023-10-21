from __future__ import annotations

from typing import TYPE_CHECKING, Any

import jinja2

from mknodes.jinja import environment
from mknodes.utils import log


if TYPE_CHECKING:
    import mknodes as mk


logger = log.get_logger(__name__)


class NodeEnvironment(environment.Environment):
    """Jinja Node environment.

    A Jinja Environment specifically for MkNode instances.

    - Sets the parent for the filters
    - Puts node context in jinja namespace
    - collects rendered nodes
    """

    def __init__(self, node: mk.MkNode, **kwargs: Any):
        """Constructor.

        Arguments:
            node: Node this environment belongs to.
            kwargs: Optional keyword arguments passed to parent
        """
        super().__init__(load_templates=True, **kwargs)
        if node.ctx.env:
            self.__dict__.update(node.ctx.env.__dict__)
            self.linked_to = node.ctx.env
            self.overlayed = True
        self.node = node
        self.rendered_nodes: list[mk.MkNode] = list()
        self.setup_environment()
        self._paths = self.get_extra_paths()
        self.add_template_path(*self._paths)

    def setup_environment(self):
        import mknodes as mk

        filters = {}
        for kls_name in mk.__all__:

            def wrapped(ctx, *args, kls_name=kls_name, **kwargs):
                kls = getattr(mk, kls_name)
                node = kls(*args, parent=self.node, **kwargs)
                self.rendered_nodes.append(node)
                return node

            filters[kls_name] = jinja2.pass_context(wrapped)
        self.filters.update(filters)
        self.globals["mknode"] = self
        self.globals["mk"] = filters

    def update_env_from_context(self):
        self.filters["get_link"] = self.node.ctx.links.get_link
        self.filters["get_url"] = self.node.ctx.links.get_url
        self.globals |= self.node.ctx.as_dict()

    def get_extra_paths(self) -> list[str]:
        import pathlib

        from mknodes.utils import inspecthelpers

        paths = []
        path = inspecthelpers.get_file(self.node.__class__)  # type: ignore[arg-type]
        assert path
        paths.append(pathlib.Path(path).parent.as_posix())
        if self.node.parent_navs:
            nav = self.node.parent_navs[-1]
            if "created" in nav.metadata:
                file = nav.metadata["created"]["source_filename"]
                path = pathlib.Path(file).parent
                paths.append(path.as_posix())
        return paths

    def render_template(
        self,
        template_name: str,
        variables: dict[str, Any] | None = None,
        parent_template: str | None = None,
    ) -> str:
        """Render a loaded template.

        Rendered nodes can be collected from `rendered_nodes` attribute after this call.

        Arguments:
            template_name: Template name
            variables: Extra variables for this render call
            parent_template: Optional parent template (to be used with super())
        """
        # if pathlib.Path(template_name).as_posix() not in self.list_templates():
        #     self.add_template(template_name)
        self.rendered_nodes = []
        self.update_env_from_context()
        return super().render_template(template_name, variables, parent_template)

    def render_string(self, markdown: str, variables: dict | None = None):
        """Render a template string.

        Rendered nodes can be collected from `rendered_nodes` attribute after this call.

        Arguments:
            markdown: String to render
            variables: Extra variables for the environment
        """
        self.rendered_nodes = []
        self.update_env_from_context()
        return super().render_string(markdown, variables)

    def set_mknodes_filters(self):
        """Set our MkNode filters."""
        import mknodes as mk

        filters = {}
        for kls_name in mk.__all__:

            def wrapped(ctx, *args, kls_name=kls_name, **kwargs):
                kls = getattr(mk, kls_name)
                node = kls(*args, parent=self.node, **kwargs)
                self.rendered_nodes.append(node)
                return node

            filters[kls_name] = jinja2.pass_context(wrapped)
        self.filters.update(filters)
        self.globals["mk"] = filters


if __name__ == "__main__":
    import mknodes as mk

    node = mk.MkText.with_default_context()
    env = NodeEnvironment(node)
    txt = "{{ metadata.required_python_version | MkAdmonition }}"
    print(env.render_string(txt))
    print(env.rendered_nodes)
    # text = env.render_string(r"{{ 'test' | MkHeader }}")
    # text = env.render_string(r"{{ 50 | MkProgressBar }}")
    # print(env.rendered_nodes)
    # env.render_string(r"{{test('hallo')}}")
