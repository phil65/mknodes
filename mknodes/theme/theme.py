from __future__ import annotations

from collections.abc import MutableMapping
import logging

from mknodes import mkdocsconfig, project
from mknodes.cssclasses import rootcss
from mknodes.pages import templateregistry
from mknodes.utils import reprhelpers, requirements


logger = logging.getLogger(__name__)


class Theme:
    """MkDocs Theme."""

    def __init__(
        self,
        theme_name: str,
        *,
        config: mkdocsconfig.Config | None = None,
        project: project.Project | None = None,
        template_registry: templateregistry.TemplateRegistry | None = None,
    ):
        self.theme_name = theme_name
        self.config = config or mkdocsconfig.Config()
        self.css = rootcss.RootCSS()
        self.templates = template_registry or templateregistry.TemplateRegistry()
        self.associated_project = project

    def get_requirements(self):
        return requirements.Requirements(
            css={"mknodes_theme.css": str(self.css)},
            templates=list(self.templates),
        )

    @classmethod
    def get_theme(cls, config: mkdocsconfig.Config, **kwargs):
        theme_name = config.theme.name
        if theme_name == "material":
            from mknodes.theme import materialtheme

            return materialtheme.MaterialTheme(**kwargs)
        return Theme(theme_name, config=config, **kwargs)

    def get_files(self):
        return {}

    def get_primary_color(self) -> str:
        return "#5555BB"

    def get_text_color(self) -> str:
        return "#000000"

    def __repr__(self):
        return reprhelpers.get_repr(self, theme_name=self.theme_name)

    def aggregate_info(self) -> dict:
        return dict(
            primary_color=self.get_primary_color(),
            text_color=self.get_text_color(),
        )

    def adapt_extensions(self, extensions: MutableMapping[str, dict]):
        pass


if __name__ == "__main__":
    theme = Theme(theme_name="material")
    print(theme)
