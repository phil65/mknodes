from __future__ import annotations

from collections.abc import MutableMapping

from mknodes import project
from mknodes.info import contexts
from mknodes.pages import templateregistry
from mknodes.utils import log, reprhelpers, requirements


logger = log.get_logger(__name__)


class Theme:
    """MkDocs Theme."""

    css_template = None

    def __init__(
        self,
        theme_name: str,
        *,
        data: dict | None = None,
        project: project.Project | None = None,
        template_registry: templateregistry.TemplateRegistry | None = None,
    ):
        self.theme_name = theme_name
        self.data = data or {}
        self.templates = template_registry or templateregistry.TemplateRegistry()
        self.associated_project = project

    def __repr__(self):
        return reprhelpers.get_repr(self, theme_name=self.theme_name)

    def get_requirements(self):
        req = []
        if self.css_template and (proj := self.associated_project):
            tmpl_ctx = self.get_template_context()
            css_text = proj.context.env.render_template(
                self.css_template,
                variables=tmpl_ctx,
            )
            req = [requirements.CSSText("mknodes_theme.css", css_text)]
        return requirements.Requirements(css=req, templates=list(self.templates))

    def get_template_context(self):
        return {}

    @classmethod
    def get_theme(cls, theme_name: str = "material", data: dict | None = None, **kwargs):
        if theme_name == "material":
            from mknodes.theme import materialtheme

            return materialtheme.MaterialTheme(data=data, **kwargs)
        return Theme(theme_name, data=data, **kwargs)

    def iter_nodes(self):
        yield from ()

    @property
    def primary_color(self) -> str:
        return "#5555BB"

    @property
    def text_color(self) -> str:
        return "#000000"

    @property
    def context(self):
        return contexts.ThemeContext(
            name=self.theme_name,
            data=self.data,
            primary_color=self.primary_color,
            text_color=self.text_color,
        )

    def adapt_extensions(self, extensions: MutableMapping[str, dict]):
        pass


if __name__ == "__main__":
    theme = Theme.get_theme("material")
    proj = project.Project.for_mknodes()
    print(theme)
