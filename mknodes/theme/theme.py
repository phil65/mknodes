from __future__ import annotations

from collections.abc import MutableMapping

from mknodes import project
from mknodes.cssclasses import rootcss
from mknodes.info import contexts
from mknodes.pages import templateregistry
from mknodes.utils import log, reprhelpers, requirements


logger = log.get_logger(__name__)


class Theme:
    """MkDocs Theme."""

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
        self.css = rootcss.RootCSS()
        self.templates = template_registry or templateregistry.TemplateRegistry()
        self.associated_project = project

    def __repr__(self):
        return reprhelpers.get_repr(self, theme_name=self.theme_name)

    def get_requirements(self):
        return requirements.Requirements(
            css={"mknodes_theme.css": str(self.css)},
            templates=list(self.templates),
        )

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
    theme = Theme(theme_name="material")
    print(theme)
