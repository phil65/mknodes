"""Writer producing an mdBook (`book.toml` + `src/` with `SUMMARY.md`).

mdBook is a Rust binary (https://rust-lang.github.io/mdBook/), not a Python package:
`mknodes generate --engine mdbook` works without it, `build` / `serve` need `mdbook` on
the PATH (`cargo install mdbook`, or a release binary).

The whole book folder (default `book/`) is generated: `book.toml`, `src/SUMMARY.md`,
the pages and assets, plus the hand-written files of the docs folder (copied into
`src/`). The HTML goes into the site dir (default `site/`). Extra `book.toml` content
comes from the `mdbook` setting (`[tool.mknodes.mdbook]` in `pyproject.toml`);
a configured `[preprocessor.admonish]` switches admonitions to the
`mdbook-admonish` syntax.
"""

import os
import shutil
from typing import TYPE_CHECKING, Any
import urllib.parse

import tomli_w

from mknodes.site.writers.base import EngineNotFoundError, GeneratedFolder, Writer
from mknodes.site.writers.zensical import EXCLUDED_DOCS, merge_values
from mknodes.utils import log


if TYPE_CHECKING:
    import pathlib

    from mknodes.build import BuildOutput, NavItem
    from mknodes.rendering import Renderer


logger = log.get_logger(__name__)

DEFAULT_BOOK_DIR = "book"
DEFAULT_SITE_DIR = "site"
SRC_DIR = "src"
CONFIG_FILE = "book.toml"
SUMMARY_FILE = "SUMMARY.md"
INDEX_NAMES = ("index.md", "README.md")
INSTALL_HINT = (
    "mdBook is not installed (no `mdbook` on the PATH). Install it with "
    "`cargo install mdbook` or a release binary from "
    "https://github.com/rust-lang/mdBook/releases, or use `mknodes generate --engine mdbook`."
)


def _escape(title: str) -> str:
    return title.replace("[", r"\[").replace("]", r"\]")


def _link(target: str) -> str:
    return target.replace(" ", "%20")


def _is_index(target: str | None) -> bool:
    return target is not None and target.rsplit("/", 1)[-1] in INDEX_NAMES


class SummaryWriter:
    """Render a nav as mdBook `SUMMARY.md`.

    mdBook differs from the literate-nav format: sections need a link (or `()` for a
    draft chapter), a file may appear only once, and only local files can be chapters.
    A section's index page becomes the section link, a top-level index page the
    (unnumbered) prefix chapter.
    """

    def __init__(self) -> None:
        self.seen: set[str] = set()
        self.skipped: list[str] = []

    def render(self, items: list[NavItem], title: str = "Summary") -> str:
        lines = [f"# {title}", ""]
        items = list(items)
        if items and not items[0].is_section and _is_index(items[0].target):
            first = items.pop(0)
            assert first.target
            self.seen.add(first.target)
            lines += [f"[{_escape(first.title)}]({_link(first.target)})", ""]
        lines += self._render_items(items, level=0)
        return "\n".join(lines) + "\n"

    def _render_items(self, items: list[NavItem], level: int) -> list[str]:
        lines: list[str] = []
        indent = "    " * level
        for item in items:
            children = list(item.children)
            target = item.target
            if item.is_section and children:
                first = children[0]
                if not first.is_section and _is_index(first.target):
                    target = first.target
                    children.pop(0)
            if target and "://" in target:
                self.skipped.append(target)  # mdBook chapters must be local files
                continue
            if target and target in self.seen:
                self.skipped.append(target)  # mdBook allows a file only once
                if not children:
                    continue
                target = None  # draft chapter holding the children
            if target:
                self.seen.add(target)
            link = _link(target) if target else ""
            lines.append(f"{indent}- [{_escape(item.title)}]({link})")
            lines += self._render_items(children, level + 1)
        return lines


def nav_to_summary(items: list[NavItem], title: str = "Summary") -> str:
    """Render the nav as mdBook `SUMMARY.md`."""
    return SummaryWriter().render(items, title)


def is_available() -> bool:
    """Return whether the `mdbook` binary is on the PATH."""
    return shutil.which("mdbook") is not None


class MdbookWriter(Writer):
    """Write a `BuildOutput` as an mdBook: `book.toml` + `src/` (pages, `SUMMARY.md`)."""

    name = "mdbook"
    flavor = "mdbook"

    @property
    def book_dir(self) -> pathlib.Path:
        """The generated book folder (`generated_dir` setting, default `book`)."""
        return self.settings.project_dir / (self.settings.generated_dir or DEFAULT_BOOK_DIR)

    @property
    def site_dir(self) -> pathlib.Path:
        """The HTML output folder (`site_dir` setting / site config, default `site`)."""
        name = self.settings.site_dir or self.settings.site_config.get("site_dir")
        return self.settings.project_dir / (name or DEFAULT_SITE_DIR)

    @property
    def extra_config(self) -> dict[str, Any]:
        """Extra `book.toml` content (`mdbook` setting)."""
        return dict(self.settings.mdbook or {})

    @property
    def uses_admonish(self) -> bool:
        preprocessors = self.extra_config.get("preprocessor") or {}
        return isinstance(preprocessors, dict) and "admonish" in preprocessors

    def get_renderer(self) -> Renderer:
        from mknodes import rendering
        from mknodes.rendering.mdbook import MdbookRenderer

        renderer = rendering.get_renderer(self.resolved_flavor)
        if isinstance(renderer, MdbookRenderer) and self.uses_admonish:
            return MdbookRenderer(admonish=True)
        return renderer

    def write(self, output: BuildOutput) -> pathlib.Path:
        book_dir = self.book_dir.resolve()
        protected = {self.settings.project_dir.resolve(), self.settings.resolved_docs_dir.resolve()}
        if book_dir in protected:
            msg = f"The mdBook folder {book_dir} must not be the project or docs folder."
            raise ValueError(msg)
        folder = GeneratedFolder(book_dir, owned=True)
        prefix = f"{SRC_DIR}/"
        docs_dir = self.settings.resolved_docs_dir
        self._mirror_docs(docs_dir, folder, output, prefix=prefix, exclude=EXCLUDED_DOCS)
        for path, content in output.files.items():
            if f"{prefix}{path}" not in folder.written:
                folder.write(f"{prefix}{path}", content)
        summary = SummaryWriter()
        text = summary.render(output.nav, self._title(output))
        folder.write(f"{prefix}{SUMMARY_FILE}", text)
        if summary.skipped:
            logger.info("Not in SUMMARY.md (external or duplicate): %s", summary.skipped)
        missing = sorted(set(output.pages) - summary.seen)
        if missing:
            logger.warning("%s pages are not in the nav (mdBook skips them)", len(missing))
            logger.debug("Pages not in the nav: %s", missing)
        config = self.build_config(output)
        folder.write(CONFIG_FILE, tomli_w.dumps(config))
        removed = folder.finish()
        if output.templates:
            logger.info("Ignoring %s theme templates (mdBook)", len(output.templates))
        logger.info(
            "Wrote %s files (%s changed, %s removed) to %s",
            len(folder.written),
            len(folder.changed),
            len(removed),
            book_dir,
        )
        self.folder = folder
        return book_dir / CONFIG_FILE

    def _title(self, output: BuildOutput) -> str:
        return (
            self.settings.site_config.get("site_name")
            or output.metadata.site_name
            or self.settings.project_dir.name
        )

    def build_config(self, output: BuildOutput) -> dict[str, Any]:
        """Return the `book.toml` content."""
        src = self.settings.site_config
        meta = output.metadata
        book: dict[str, Any] = {"title": self._title(output), "src": SRC_DIR}
        if author := src.get("site_author") or meta.site_author:
            book["authors"] = [author]
        if description := src.get("site_description") or meta.site_description:
            book["description"] = description
        site_dir = os.path.relpath(self.site_dir, self.book_dir)
        html: dict[str, Any] = {"no-section-label": True}
        if repo_url := src.get("repo_url") or meta.repo_url:
            html["git-repository-url"] = repo_url
        if site_url := src.get("site_url"):
            # mdBook wants the path the book is served under (for the 404 page).
            html["site-url"] = urllib.parse.urlsplit(site_url).path or "/"
        if css := [f"{SRC_DIR}/{c}" for c in output.extra_css if "://" not in c]:
            html["additional-css"] = css
        if js := [f"{SRC_DIR}/{s.path}" for s in output.extra_javascript if "://" not in s.path]:
            html["additional-js"] = js
        config: dict[str, Any] = {
            "book": book,
            "build": {"build-dir": site_dir.replace(os.sep, "/"), "create-missing": False},
            "output": {"html": html},
        }
        return merge_values(config, self.extra_config)

    def ensure_available(self) -> None:
        if not is_available():
            raise EngineNotFoundError(INSTALL_HINT)

    def build_command(
        self, *, serve: bool = False, extra_args: list[str] | None = None
    ) -> list[str]:
        self.ensure_available()
        args = list(extra_args or [])
        if "--strict" in args:
            logger.warning("mdBook has no strict mode, ignoring --strict")
            args.remove("--strict")
        return ["mdbook", "serve" if serve else "build", str(self.book_dir), *args]
