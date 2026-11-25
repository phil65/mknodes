"""Writer producing a MkDocs project (Material for MkDocs theme).

Zensical reads MkDocs configs, so this is the Zensical writer with MkDocs as the engine:
the generated pages go into the docs folder and a generated config
(`mkdocs.generated.yml`) `INHERIT`s the project's `mkdocs.yml`.
Build with `mkdocs build -f mkdocs.generated.yml` (or `mknodes build --engine mkdocs`).
Needs the `mkdocs` extra (`mkdocs`, `mkdocs-material`).
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from mknodes.site.writers.base import EngineNotFoundError
from mknodes.site.writers.zensical import ZensicalWriter, _has_module


if TYPE_CHECKING:
    from mknodes.build import BuildOutput


INSTALL_HINT = (
    "MkDocs is not installed. Install the `mkdocs` extra (`mknodes[mkdocs]`: mkdocs, "
    "mkdocs-material) or use the default engine (Zensical)."
)
# Plugin entries MkDocs can't load: the former `mkdocs-mknodes` plugin entry still holds
# the generator settings of many sites (Zensical ignores plugins it doesn't know).
IGNORED_PLUGINS = {"mknodes"}


def _plugin_name(entry: Any) -> str | None:
    if isinstance(entry, str):
        return entry
    if isinstance(entry, dict) and len(entry) == 1:
        return next(iter(entry))
    return None


class MkDocsWriter(ZensicalWriter):
    """Write a `BuildOutput` as MkDocs input: docs folder + generated config."""

    name = "mkdocs"
    module = "mkdocs"
    theme_package = "material"

    def build_config(
        self,
        output: BuildOutput,
        *,
        templates_dir: str | None = None,
        social: list[dict[str, str]] | None = None,
    ) -> dict[str, Any]:
        cfg = super().build_config(output, templates_dir=templates_dir, social=social)
        plugins = self.source_config.get("plugins")
        if isinstance(plugins, dict):
            plugins = [{k: v} if v is not None else k for k, v in plugins.items()]
        if isinstance(plugins, list) and any(_plugin_name(p) in IGNORED_PLUGINS for p in plugins):
            # INHERIT replaces lists, so the generated list wins.
            cfg["plugins"] = [p for p in plugins if _plugin_name(p) not in IGNORED_PLUGINS]
        return cfg

    def ensure_available(self) -> None:
        if not (_has_module("mkdocs") and _has_module("material")):
            raise EngineNotFoundError(INSTALL_HINT)

    def build_command(
        self, *, serve: bool = False, extra_args: list[str] | None = None
    ) -> list[str]:
        self.ensure_available()
        return super().build_command(serve=serve, extra_args=extra_args)
