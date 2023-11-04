from __future__ import annotations

from typing import Any

import jinja2
import jinjarope

from jinjarope import loaders

from mknodes.utils import jinjahelpers, log


logger = log.get_logger(__name__)


class Environment(jinjarope.Environment):
    """An enhanced Jinja environment."""

    def __init__(
        self,
        *,
        loader: jinja2.BaseLoader
        | list[jinja2.BaseLoader]
        | dict
        | list[dict]
        | None = None,
        load_templates: bool = False,
        **kwargs: Any,
    ):
        """Constructor.

        Arguments:
            loader: Loader to use (Also accepts a JSON representation of loaders)
            load_templates: Adds additional loaders to the env (deprecated).
            kwargs: Keyword arguments passed to parent
        """
        loader = loaders.from_json(loader)
        resource_loader = jinjarope.ChoiceLoader(
            [
                jinjarope.get_loader("docs/"),
                jinjarope.FsSpecProtocolPathLoader(),
            ]
        )

        if load_templates and loader:
            kwargs["loader"] = resource_loader | loader
        elif load_templates:
            kwargs["loader"] = resource_loader
        else:
            kwargs["loader"] = loader
        super().__init__(**kwargs)
        self.filters.update(jinjahelpers.get_filters())
        self.globals.update(jinjahelpers.get_globals())


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
