from __future__ import annotations

import logging

import jinja2

from mknodes.utils import yamlhelpers


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

    def __init__(self, undefined: str = "silent", load_templates: bool = False):
        if load_templates:
            loader = jinja2.FileSystemLoader(searchpath="mknodes/resources")
        else:
            loader = None
        behavior = UNDEFINED_BEHAVIOR[undefined]
        self.env = jinja2.Environment(undefined=behavior, loader=loader)
        self.variables = {}
        filters = {"dump_yaml": yamlhelpers.dump_yaml}
        import mknodes

        for kls_name in mknodes.__all__:
            filters[kls_name] = getattr(mknodes, kls_name)
        self.env.filters.update(filters)

    def render(self, markdown: str, variables=None):
        try:
            template = self.env.from_string(markdown)
        except jinja2.exceptions.TemplateSyntaxError as e:
            logger.warning("Error when loading template: %s", e)
            return markdown
        variables = self.variables | (variables or {})
        return template.render(**variables)

    def render_template(self, template_name: str, variables=None):
        template = self.env.get_template(template_name)
        variables = self.variables | (variables or {})
        return template.render(**variables)


if __name__ == "__main__":
    env = Environment(load_templates=True)
    env.env.get_template("macros_info.md")
    text = env.render("{{test}}", dict(test="fkj"))
    print(text)
