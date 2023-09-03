from __future__ import annotations

import logging

import jinja2


logger = logging.getLogger(__name__)


class LaxUndefined(jinja2.Undefined):
    """Pass anything wrong as blank."""

    def _fail_with_undefined_error(self, *args, **kwargs):
        return ""


UNDEFINED_BEHAVIOR = {
    "keep": jinja2.DebugUndefined,
    "silent": jinja2.Undefined,
    "strict": jinja2.StrictUndefined,
    # lax will even pass unknown objects:
    "lax": LaxUndefined,
}


class Environment:
    """MkNodes Environment."""

    def __init__(self):
        self.env = jinja2.Environment(undefined=UNDEFINED_BEHAVIOR["silent"])

    def render(self, markdown: str, variables=None):
        try:
            md_template = self.env.from_string(markdown)
        except jinja2.exceptions.TemplateSyntaxError as e:
            logger.warning("Error when rendering markdown: %s", e)
            return markdown
        variables = variables or {}
        return md_template.render(**variables)


if __name__ == "__main__":
    builder = Environment()
    builder.render("{{test}}")
    print(builder)
