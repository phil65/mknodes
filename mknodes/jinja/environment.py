from __future__ import annotations

from collections.abc import Mapping
import contextlib
import functools
import os

from typing import TYPE_CHECKING, Any

import jinja2

from mknodes.utils import jinjahelpers, log, mergehelpers


if TYPE_CHECKING:
    import mknodes as mk


logger = log.get_logger(__name__)


class Environment(jinja2.Environment):
    """Jinja environment."""

    def __init__(self, *, undefined: str = "silent", load_templates: bool = False):
        """Constructor.

        Arguments:
            undefined: Handling of "Undefined" errors
            load_templates: Whether to load the templates into environment.
        """
        loader = jinjahelpers.resource_loader if load_templates else None
        behavior = jinjahelpers.UNDEFINED_BEHAVIOR[undefined]
        self.extra_files: set[str] = set()
        self.extra_paths: set[str] = set()
        super().__init__(undefined=behavior, loader=loader, trim_blocks=True)
        self.filters.update(jinjahelpers.ENVIRONMENT_FILTERS)
        self.globals.update(jinjahelpers.ENVIRONMENT_GLOBALS)
        self.rendered_nodes: list[mk.MkNode] = list()

    def merge_globals(self, other: Mapping, additive: bool = False):
        """Merge other into the environment globals with given strategy.

        Arguments:
            other: Globals to merge into environment
            additive: Whether an additive strategy should be used instead of replace.
        """
        strategy = "additive" if additive else "replace"
        mapping = mergehelpers.merge_dicts(self.variables, other, strategy=strategy)
        self.variables = dict(mapping)

    def render_string(self, markdown: str, variables: dict | None = None):
        """Render a template string.

        Arguments:
            markdown: String to render
            variables: Extra variables for the environment
        """
        try:
            template = self.from_string(markdown)
        except jinja2.exceptions.TemplateSyntaxError:
            logger.exception("Error when loading template.")
            return markdown
        variables = variables or {}
        try:
            return template.render(**variables)
        except jinja2.exceptions.UndefinedError:
            logger.exception("Error when rendering template.")
            return ""

    def add_template(self, file: str | os.PathLike):
        """Add a new template during runtime.

        Will create a new DictLoader and inject it into the existing loaders.

        Useful since render_string/render_file does not allow to use a parent template.
        Using this, render_template can be used.

        Arguments:
            file: File to add as a template
        """
        # we keep track of already added extra files to not add things multiple times.
        file = str(file)
        if file in self.extra_files:
            return
        self.extra_files.add(file)
        content = jinjahelpers.load_file(file)
        new_loader = jinja2.DictLoader({file: content})
        self._add_loader(new_loader)

    def add_template_path(self, path: str | os.PathLike | list[str]):
        """Add a new template path runtime.

        Will append a new FileSystemLoader by wrapping it and the the current loader into
        either an already-existing or a new Choiceloader.

        Arguments:
            path: Template serch patch to add
        """
        path = str(path)
        if path in self.extra_paths:
            return
        self.extra_paths.add(path)
        new_loader = jinja2.FileSystemLoader(path)
        self._add_loader(new_loader)

    def _add_loader(self, new_loader):
        match self.loader:
            case jinja2.ChoiceLoader():
                self.loader.loaders = [new_loader, *self.loader.loaders]
            case None:
                self.loader = new_loader
            case _:
                self.loader = jinja2.ChoiceLoader(loaders=[new_loader, self.loader])

    def render_file(self, file: str | os.PathLike, variables: dict | None = None) -> str:
        """Helper to directly render a template from filesystem.

        Note: The file we pull in gets cached. That should be fine for our case though.

        Arguments:
            file: Template file to load
            variables: Extra variables for the environment
        """
        content = jinjahelpers.load_file(str(file))
        return self.render_string(content, variables)

    def render_template(
        self,
        template_name: str,
        variables: dict[str, Any] | None = None,
        parent_template: str | None = None,
    ):
        """Render a loaded template.

        Arguments:
            template_name: Template name
            variables: Extra variables for this render call
            parent_template: Optional parent template (to be used with super())
        """
        template = self.get_template(template_name, parent=parent_template)
        variables = variables or {}
        return template.render(**variables)

    @contextlib.contextmanager
    def with_globals(self, **kwargs: Any):
        """Context manager to temporarily set globals for the environment.

        Arguments:
            kwargs: Globals to set
        """
        temp = {}
        for k, v in kwargs.items():
            temp[k] = self.globals.get(k)
            self.globals[k] = v
        yield
        self.globals.update(temp)

    @contextlib.contextmanager
    def with_fence(
        self,
        start_variable: str = r"{{",
        end_variable: str = r"}}",
        start_block: str = "{%",
        end_block: str = "%}",
    ):
        """Context manager to temporarily set custom fences for jinja blocks.

        Arguments:
            start_variable: The string marking the beginning of a print statement
            end_variable: The string marking the end of a print statement
            start_block: The string marking the end of a block
            end_block: The string marking the end of a block
        """
        old_start_block = self.block_start_string
        old_end_block = self.block_end_string
        old_start_var = self.variable_start_string
        old_end_var = self.variable_end_string
        self.block_start_string = start_block
        self.block_end_string = end_block
        self.variable_start_string = start_variable
        self.variable_end_string = end_variable
        yield
        self.block_start_string = old_start_block
        self.block_end_string = old_end_block
        self.variable_start_string = old_start_var
        self.variable_end_string = old_end_var

    def set_mknodes_filters(self, parent: mk.MkNode | None = None):
        """Set our MkNode filters.

        The filters are a partial with the parent already set, if parent is given.

        Arguments:
            parent: Node parent
        """
        import mknodes

        filters = {}
        for kls_name in mknodes.__all__:
            if parent is not None:
                kls = getattr(mknodes, kls_name)
                fn = functools.partial(kls, parent=parent)
            else:
                fn = getattr(mknodes, kls_name)

            def wrapped(ctx, *args, fn=fn, **kwargs):
                node = fn(*args, **kwargs)
                self.rendered_nodes.append(node)
                return node

            new = functools.partial(wrapped, fn=fn)
            filters[kls_name] = jinja2.pass_context(new)
        self.filters.update(filters)
        # self.globals.update(filters)


if __name__ == "__main__":
    # from mknodes.project import Project

    env = Environment()
    env.set_mknodes_filters()
    text = env.render_string(r"{{ 'test' | MkHeader }}")
    text = env.render_string(r"{{ 'test' | MkText }}")
    print(env.rendered_nodes)
    # print(text)
    # env.render_string(r"{{test('hallo')}}")

    # proj = Project.for_mknodes()
    # ctx = proj.context.as_dict()
    # env.globals.update(ctx)
    # text = env.render_string("{{ 'TTset' | isinstance(str) }}")
    # print(text)
