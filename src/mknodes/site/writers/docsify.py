"""Writer producing a Docsify site (`index.html` + `_sidebar.md` + the Markdown pages).

[Docsify](https://docsify.js.org) renders Markdown in the browser, so there is no build
step: the written folder is the website. `index.html` loads Docsify (a pinned version)
from a CDN, `_sidebar.md` holds the nav. Pages use the GitHub flavour (Docsify 5 renders
GitHub alerts, raw HTML and `.md` links).

The folder (the `site_dir` setting / `-d`, default `site/`; `generated_dir` for
`generate`) is fully generated: pages, assets and the hand-written files of the docs
folder. `serve` runs a static file server (Python's `http.server`).
"""

from __future__ import annotations

import html
import json
import sys
from typing import TYPE_CHECKING, Any

from mknodes.site.writers.base import GeneratedFolder, Writer
from mknodes.site.writers.zensical import EXCLUDED_DOCS, merge_values
from mknodes.utils import log


if TYPE_CHECKING:
    import pathlib

    from mknodes.build import BuildOutput, NavItem


logger = log.get_logger(__name__)

DOCSIFY_VERSION = "5.1.0"
PRISM_VERSION = "1.30.0"
CDN = "https://cdn.jsdelivr.net/npm"
DEFAULT_SITE_DIR = "site"
SIDEBAR_FILE = "_sidebar.md"
INDEX_FILE = "index.html"
HOMEPAGE = "index.md"
SERVE_PORT = 3000
# Prism languages loaded besides Docsify's bundled ones (markup, css, clike, javascript).
PRISM_LANGUAGES = ("python", "bash", "toml", "yaml", "json", "diff", "markdown", "rust")


def _link(target: str) -> str:
    if "://" in target:
        return target
    return "/" + target.replace(" ", "%20")  # absolute: the sidebar is used on every page


def nav_to_sidebar(items: list[NavItem], level: int = 0) -> str:
    """Render the nav as Docsify `_sidebar.md` (nested list, sections as plain items)."""
    lines: list[str] = []
    indent = "  " * level
    for item in items:
        title = item.title.replace("[", r"\[").replace("]", r"\]")
        if item.is_section:
            lines.append(f"{indent}- {title}")
            if item.children:
                lines.append(nav_to_sidebar(item.children, level + 1).rstrip("\n"))
        else:
            assert item.target
            lines.append(f"{indent}- [{title}]({_link(item.target)})")
    return "\n".join(lines) + "\n"


class DocsifyWriter(Writer):
    """Write a `BuildOutput` as a Docsify site (no build step)."""

    name = "docsify"
    flavor = "github"

    @property
    def site_dir(self) -> pathlib.Path:
        """The site folder (`generated_dir`, else `site_dir` / site config, default `site`)."""
        name = (
            self.settings.generated_dir
            or self.settings.site_dir
            or self.settings.site_config.get("site_dir")
        )
        return self.settings.project_dir / (name or DEFAULT_SITE_DIR)

    @property
    def extra_config(self) -> dict[str, Any]:
        """Extra `window.$docsify` options (`docsify` setting)."""
        return dict(self.settings.docsify or {})

    def write(self, output: BuildOutput) -> pathlib.Path:
        site_dir = self.site_dir.resolve()
        protected = {self.settings.project_dir.resolve(), self.settings.resolved_docs_dir.resolve()}
        if site_dir in protected:
            msg = f"The Docsify folder {site_dir} must not be the project or docs folder."
            raise ValueError(msg)
        folder = GeneratedFolder(site_dir, owned=True)
        self._mirror_docs(self.settings.resolved_docs_dir, folder, output, exclude=EXCLUDED_DOCS)
        for path, content in output.files.items():
            if path not in folder.written:
                folder.write(path, content)
        folder.write(SIDEBAR_FILE, nav_to_sidebar(output.nav))
        folder.write(".nojekyll", "")  # GitHub Pages (branch deploys) skips `_` files otherwise
        folder.write(INDEX_FILE, self.render_index(output))
        removed = folder.finish()
        if output.templates:
            logger.info("Ignoring %s theme templates (Docsify)", len(output.templates))
        logger.info(
            "Wrote %s files (%s changed, %s removed) to %s",
            len(folder.written),
            len(folder.changed),
            len(removed),
            site_dir,
        )
        self.folder = folder
        return site_dir / INDEX_FILE

    def _title(self, output: BuildOutput) -> str:
        return (
            self.settings.site_config.get("site_name")
            or output.metadata.site_name
            or self.settings.project_dir.name
        )

    def build_config(self, output: BuildOutput) -> dict[str, Any]:
        """Return the `window.$docsify` options."""
        src = self.settings.site_config
        config: dict[str, Any] = {
            "name": self._title(output),
            "homepage": HOMEPAGE,
            "loadSidebar": True,
            "alias": {"/.*/_sidebar.md": f"/{SIDEBAR_FILE}"},
            "relativePath": True,
            "subMaxLevel": 2,
            "auto2top": True,
            "search": {"paths": "auto", "depth": 3},
        }
        if repo_url := src.get("repo_url") or output.metadata.repo_url:
            config["repo"] = repo_url
        return merge_values(config, self.extra_config)

    def render_index(self, output: BuildOutput) -> str:
        """Return `index.html`: Docsify, its search plugin, Prism languages, extra CSS / JS."""
        title = html.escape(self._title(output))
        description = self.settings.site_config.get("site_description")
        description = description or output.metadata.site_description or ""
        base = f"{CDN}/docsify@{DOCSIFY_VERSION}/dist"
        css = [f"{base}/themes/core.min.css", *output.extra_css]
        scripts = [
            f"{base}/docsify.min.js",
            f"{base}/plugins/search.min.js",
            *(
                f"{CDN}/prismjs@{PRISM_VERSION}/components/prism-{lang}.min.js"
                for lang in PRISM_LANGUAGES
            ),
            *(s.path for s in output.extra_javascript),
        ]
        config = json.dumps(self.build_config(output), indent=2).replace("</", "<\\/")
        links = "\n".join(f'    <link rel="stylesheet" href="{html.escape(c)}">' for c in css)
        tags = "\n".join(f'    <script src="{html.escape(s)}"></script>' for s in scripts)
        return f"""\
<!DOCTYPE html>
<html lang="en">
  <head>
    <!-- Generated by mknodes (`--engine docsify`). Do not edit: regenerated on every build. -->
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{title}</title>
    <meta name="description" content="{html.escape(description)}">
{links}
  </head>
  <body>
    <div id="app"></div>
    <script>
      window.$docsify = {config};
    </script>
{tags}
  </body>
</html>
"""

    def build_command(
        self, *, serve: bool = False, extra_args: list[str] | None = None
    ) -> list[str] | None:
        if not serve:
            return None  # the written folder is the website
        port = str(SERVE_PORT)
        return [sys.executable, "-m", "http.server", "--directory", str(self.site_dir), port]
