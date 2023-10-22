from __future__ import annotations

from collections.abc import Mapping
import contextlib
import os
import pathlib

from typing import Any

import jinja2

from mknodes.jinja import loaders, undefined as undefined_
from mknodes.utils import jinjahelpers, log, mergehelpers, pathhelpers


logger = log.get_logger(__name__)


class Environment(jinja2.Environment):
    """An enhanced Jinja environment."""

    def __init__(
        self,
        *,
        undefined: undefined_.UndefinedStr | type[jinja2.Undefined] = "strict",
        trim_blocks: bool = True,
        load_templates: bool = False,
        **kwargs: Any,
    ):
        """Constructor.

        Arguments:
            undefined: Handling of "Undefined" errors
            trim_blocks: Whitespace handling. Changes jinja default to `True`.
            load_templates: Whether to load the templates into environment.
            kwargs: Keyword arguments passed to parent
        """
        loader = loaders.resource_loader if load_templates else None
        if isinstance(undefined, str):
            undefined = undefined_.UNDEFINED_BEHAVIOR[undefined]
        self._extra_files: set[str] = set()
        self._extra_paths: set[str] = set()
        super().__init__(
            undefined=undefined,
            loader=loader,
            trim_blocks=trim_blocks,
            **kwargs,
        )
        self.filters.update(jinjahelpers.get_filters())
        self.globals.update(jinjahelpers.get_globals())
        self.filters["render_template"] = self.render_template
        self.filters["render_string"] = self.render_string
        self.filters["render_file"] = self.render_file

    def __contains__(self, template: str | os.PathLike):
        return pathlib.Path(template).as_posix() in self.list_templates()

    def __getitem__(self, val: str) -> jinja2.Template:
        return self.get_template(val)

    def inherit_from(self, env: jinja2.Environment):
        self.__dict__.update(env.__dict__)
        self.linked_to = env
        self.overlayed = True

    def merge_globals(self, other: Mapping, additive: bool = False):
        """Merge other into the environment globals with given strategy.

        Arguments:
            other: Globals to merge into environment
            additive: Whether an additive strategy should be used instead of replace.
        """
        strategy = "additive" if additive else "replace"
        mapping = mergehelpers.merge_dicts(self.variables, other, strategy=strategy)
        self.variables = dict(mapping)

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
        if file in self._extra_files:
            return
        self._extra_files.add(file)
        content = pathhelpers.load_file_cached(file)
        new_loader = loaders.DictLoader({file: content})
        self._add_loader(new_loader)

    def add_template_path(self, *path: str | os.PathLike):
        """Add a new template path during runtime.

        Will append a new FileSystemLoader by wrapping it and the the current loader into
        either an already-existing or a new Choiceloader.

        Arguments:
            path: Template serch path(s) to add
        """
        for p in path:
            if p in self._extra_paths:
                return
            self._extra_paths.add(str(p))
            new_loader = loaders.FileSystemLoader(p)
            self._add_loader(new_loader)

    def _add_loader(self, new_loader: jinja2.BaseLoader | dict | str | os.PathLike):
        match new_loader:
            case dict():
                new_loader = loaders.DictLoader(new_loader)
            case str() | os.PathLike():
                new_loader = loaders.FileSystemLoader(new_loader)
        match self.loader:
            case jinja2.ChoiceLoader():
                self.loader.loaders = [new_loader, *self.loader.loaders]
            case None:
                self.loader = new_loader
            case _:
                self.loader = loaders.ChoiceLoader(loaders=[new_loader, self.loader])

    def render_string(self, markdown: str, variables: dict | None = None):
        """Render a template string.

        Arguments:
            markdown: String to render
            variables: Extra variables for the environment
        """
        template = self.from_string(markdown)
        variables = variables or {}
        return template.render(**variables)

    def render_file(self, file: str | os.PathLike, variables: dict | None = None) -> str:
        """Helper to directly render a template from filesystem.

        Note: The file we pull in gets cached. That should be fine for our case though.

        Arguments:
            file: Template file to load
            variables: Extra variables for the environment
        """
        content = pathhelpers.load_file_cached(str(file))
        return self.render_string(content, variables)

    def render_template(
        self,
        template_name: str,
        variables: dict[str, Any] | None = None,
        block_name: str | None = None,
        parent_template: str | None = None,
    ) -> str:
        """Render a loaded template (or a block of a template).

        Arguments:
            template_name: Template name
            variables: Extra variables for this render call
            block_name: Render specific block from the template
            parent_template: Optional parent template (to be used with super())
        """
        template = self.get_template(template_name, parent=parent_template)
        if not block_name:
            variables = variables or {}
            return template.render(**variables)
        try:
            block_render_func = template.blocks[block_name]
        except KeyError:
            raise BlockNotFoundError(block_name, template_name) from KeyError

        ctx = template.new_context(variables or {})
        return self.concat(block_render_func(ctx))  # type: ignore
        # except Exception:
        #     self.handle_exception()

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


class BlockNotFoundError(Exception):
    def __init__(
        self,
        block_name: str,
        template_name: str,
        message: str | None = None,
    ):
        self.block_name = block_name
        self.template_name = template_name
        super().__init__(
            message
            or f"Block {self.block_name!r} not found in template {self.template_name!r}",
        )


if __name__ == "__main__":
    env = Environment()
    txt = """{% filter styled(bold=True) %}
    test
    {% endfilter %}
    """
    print(env.render_string(txt))
    # text = env.render_string(r"{{ 'test' | MkHeader }}")
    # text = env.render_string(r"{{ 50 | MkProgressBar }}")
    # env.render_string(r"{{test('hallo')}}")
