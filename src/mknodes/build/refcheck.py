"""Check `[title][identifier]` cross-references (autorefs) of generated pages.

Static site engines (Zensical, MkDocs + autorefs) resolve `[title][dotted.path]` links
only if some page renders the object with mkdocstrings (`::: dotted.path`) or if an
inventory knows it. Otherwise they report the reference at build time, without telling
which node / template / docstring produced it.

This module does the same check on the rendered Markdown of a `BuildOutput`, cheaply
(no rendering, only griffe lookups) and reports each problem with its origin:

- Markdown of the pages: references outside of code, attributed to the node (and the
  template / source file + line) that produced them.
- Docstrings of the objects rendered by mkdocstrings (they are rendered by the engine,
  so their references are not part of the page Markdown).

The check is conservative: only dotted Python paths of packages documented on the site
(top-level package of a `:::` block, or `packages`) get validated, so links to heading
slugs or to other projects never produce false positives.
"""

from collections import Counter
import dataclasses
import difflib
import inspect
import pathlib
import posixpath
import re
from typing import TYPE_CHECKING, Any
import urllib.parse

from mknodes.info import grifferegistry
from mknodes.utils import log


if TYPE_CHECKING:
    from collections.abc import Container, Iterable, Iterator, Mapping

    import griffe

    import mknodes as mk
    from mknodes.build.output import BuildOutput


logger = log.get_logger(__name__)

# `[title][identifier]`, title may contain one level of brackets (`[`a[b]`][x]`).
REF_RE = re.compile(r"(?<![\]\\])\[((?:[^\[\]\n]|\[[^\[\]\n]*\])*)\]\[([^\[\]\s]*)\]")
# Only dotted Python paths get validated (not heading slugs / other autorefs ids).
DOTTED_PATH_RE = re.compile(r"[A-Za-z_]\w*(?:\.[A-Za-z_]\w*)+")
DIRECTIVE_RE = re.compile(r"^(?P<indent>[ \t]*)::: +(?P<identifier>\S+)\s*$")
LABEL_DEF_RE = re.compile(r"^[ \t]{0,3}\[([^\]]+)\]:\s")
FENCE_RE = re.compile(r"^[ \t]*(?P<fence>`{3,}|~{3,})")
# MyST directives in backtick fences whose content is Markdown (`{note}`, `{tab-item}`),
# unlike code-like ones (`{code-block}`, `{toctree}`, ...).
MARKDOWN_DIRECTIVE_RE = re.compile(
    r"^[ \t]*`{3,}\{(?!(?:code-block|code|sourcecode|literalinclude|toctree|math|raw"
    r"|eval-rst|mermaid)\})[\w-]+\}"
)
INLINE_CODE_RE = re.compile(r"(`+)(?:(?!\1).)+?\1")
HTML_OPEN_RE = re.compile(r"<div\b", re.IGNORECASE)
HTML_CLOSE_RE = re.compile(r"</div\s*>", re.IGNORECASE)


@dataclasses.dataclass(frozen=True)
class RefIssue:
    """An unresolvable `[title][identifier]` reference."""

    identifier: str
    """The referenced identifier."""
    title: str
    """The link text."""
    page: str
    """Path of the page containing the reference (relative to the docs root)."""
    reason: str
    """Why the reference can't be resolved."""
    line: int | None = None
    """Line in the generated page Markdown (None for references in docstrings)."""
    origin: str | None = None
    """Where the reference comes from (`file:line` of a template / source / docstring)."""
    node: str | None = None
    """The node that produced the reference."""
    suggestion: str | None = None
    """An identifier which would resolve."""
    fixable: bool = False
    """Whether `suggestion` is the same object (a path engines know), see `fix_references`."""

    def __str__(self) -> str:
        where = f"{self.page}:{self.line}" if self.line else self.page
        text = f"{where}: unresolved reference [{self.title}][{self.identifier}]"
        details = [d for d in (self.origin, self.node) if d]
        if details:
            text += f" (from {', '.join(details)})"
        text += f": {self.reason}"
        if self.suggestion:
            text += f". Did you mean `{self.suggestion}`?"
        return text


@dataclasses.dataclass
class _Directive:
    identifier: str
    page: str
    anchored: bool
    """Whether the root object gets an anchor (no heading / TOC entry -> no anchor)."""


def iter_markdown_lines(markdown: str) -> Iterator[tuple[int, str]]:
    """Yield (line number, line) of the lines outside fenced code blocks.

    Like `pymdownx.superfences`, a fence only gets closed by the same fence string.
    Inline code spans are blanked out (same length, so columns stay valid).

    Args:
        markdown: Markdown text
    """
    fence: str | None = None
    directives: list[str] = []  # open MyST directive fences with Markdown content
    for i, line in enumerate(markdown.splitlines(), start=1):
        if match := FENCE_RE.match(line):
            marker = match["fence"]
            if fence is None:
                if MARKDOWN_DIRECTIVE_RE.match(line):
                    directives.append(marker)
                elif directives and marker == directives[-1] and not line.strip(" \t`"):
                    directives.pop()
                else:
                    fence = marker
                continue
            if marker == fence and not line.strip(" \t" + marker[0]):
                fence = None
                continue
        if fence is not None:
            continue
        yield i, INLINE_CODE_RE.sub(lambda m: " " * len(m[0]), line)


def find_references(markdown: str) -> Iterator[tuple[int, str, str]]:
    """Yield (line number, title, identifier) of the `[title][identifier]` refs.

    References inside code and references to link definitions of the page
    (`[label]: url`) are skipped.

    Args:
        markdown: Markdown text
    """
    lines = list(iter_markdown_lines(markdown))
    labels = {m[1].lower() for _, line in lines if (m := LABEL_DEF_RE.match(line))}
    for lineno, line in lines:
        for match in REF_RE.finditer(line):
            title, identifier = match[1], match[2] or match[1]
            if identifier.lower() not in labels:
                yield lineno, title, identifier


def find_directives(markdown: str, page: str = "") -> list[_Directive]:
    """Return the mkdocstrings blocks (`::: identifier` + options) of given Markdown.

    Blocks inside code or raw HTML blocks are skipped (they don't get rendered).

    Args:
        markdown: Markdown text
        page: Page path (for reporting)
    """
    lines = list(iter_markdown_lines(markdown))
    directives = []
    html_depth = 0
    for idx, (_, line) in enumerate(lines):
        # mkdocstrings does not render blocks inside raw HTML (`<div markdown="1">`)
        html_depth += len(HTML_OPEN_RE.findall(line)) - len(HTML_CLOSE_RE.findall(line))
        html_depth = max(html_depth, 0)
        if html_depth or not (match := DIRECTIVE_RE.match(line)):
            continue
        indent = len(match["indent"])
        options: list[str] = []
        for _, opt_line in lines[idx + 1 :]:  # the indented options block
            if not opt_line.strip() or len(opt_line) - len(opt_line.lstrip()) <= indent:
                break
            options.append(opt_line.strip().lower())
        hidden = "show_root_toc_entry: false" in options
        anchored = not hidden or "show_root_heading: true" in options
        directives.append(_Directive(match["identifier"], page, anchored))
    return directives


def _resolve(identifier: str) -> griffe.Object | griffe.Alias | None:
    """Return the griffe object for given dotted path (None if it doesn't exist)."""
    top, _, rest = identifier.partition(".")
    try:
        module = grifferegistry.get_module(top)
        return module[rest] if rest else module
    except Exception:  # noqa: BLE001
        return None


def _canonical(obj: griffe.Object | griffe.Alias) -> str | None:
    """Return the canonical path, None for inherited members (not rendered by default)."""
    try:
        inherited = getattr(obj, "inherited", False)
        canonical = obj.canonical_path
    except Exception:  # noqa: BLE001
        return None
    return None if inherited else canonical


def _is_module(obj: griffe.Object | griffe.Alias) -> bool:
    try:
        return obj.is_module
    except Exception:  # noqa: BLE001
        return False


def _docstring(obj: griffe.Object | griffe.Alias) -> tuple[str, str | None]:
    """Return docstring text and `file:line` of given object (empty if not resolvable)."""
    try:
        doc = obj.docstring
        filepath = obj.filepath
    except Exception:  # noqa: BLE001
        return "", None
    if doc is None:
        return "", None
    path = filepath[0] if isinstance(filepath, list) else filepath
    return doc.value, f"{_short_path(path)}:{doc.lineno}"


def _short_path(path: str | pathlib.Path) -> str:
    """Return path relative to the working directory if possible."""
    path = pathlib.Path(path)
    try:
        return path.resolve().relative_to(pathlib.Path.cwd()).as_posix()
    except ValueError:
        return path.as_posix()


class RefChecker:
    """Collects the anchors mkdocstrings will create and validates references against them.

    Usage: `add_page()` for every page (collects `:::` blocks), then `check()`.
    """

    def __init__(
        self,
        packages: Iterable[str] = (),
        inventory: Container[str] | None = None,
    ) -> None:
        """Constructor.

        Args:
            packages: Top-level packages whose references get validated (in addition to
                      the packages of the `:::` blocks).
            inventory: Identifiers known from inventories (always resolvable).
        """
        self.packages = {p for p in packages if p}
        self.inventory = inventory
        self.pages: dict[str, str] = {}
        self.directives: list[_Directive] = []
        self.literal: set[str] = set()
        """Identifiers rendered with exactly this path (root blocks + their members)."""
        self.canonical: set[str] = set()
        """Canonical paths of everything rendered (aliases of them resolve, too)."""
        self.rendered: dict[str, tuple[griffe.Object | griffe.Alias, str]] = {}
        """Canonical path -> (griffe object, page) for the docstring check."""
        self.shortest: dict[str, str] = {}
        """Canonical path -> shortest rendered path of the object (for suggestions)."""
        self._collected = False

    def add_page(self, path: str, markdown: str) -> None:
        """Register a page (its mkdocstrings blocks and its references).

        Args:
            path: Page path relative to the docs root
            markdown: Generated Markdown of the page
        """
        self.pages[path] = markdown
        self.directives.extend(find_directives(markdown, path))
        self._collected = False

    def _collect(self) -> None:
        if self._collected:
            return
        for directive in self.directives:
            self.packages.add(directive.identifier.split(".")[0])
            if (obj := _resolve(directive.identifier)) is None:
                continue
            if directive.anchored:
                self._add(directive.identifier, _canonical(obj))
            self._add_members(obj, directive.identifier, directive.page, root=True)
        self._collected = True

    def _add_members(
        self,
        obj: griffe.Object | griffe.Alias,
        path: str,
        page: str,
        root: bool = False,
    ) -> None:
        canonical = _canonical(obj)
        if canonical and canonical not in self.rendered:
            self.rendered[canonical] = (obj, page)
        elif not root:
            return  # already walked (rendered on another page)
        try:
            members = dict(obj.members)
        except Exception:  # noqa: BLE001
            return
        for name, member in members.items():
            try:
                if member.is_module or (member.is_alias and obj.is_module):
                    continue  # submodules / imports are not rendered by default
            except Exception:  # noqa: BLE001
                continue
            self._add(f"{path}.{name}", _canonical(member))
            self._add_members(member, f"{path}.{name}", page)

    def _add(self, path: str, canonical: str | None) -> None:
        self.literal.add(path)
        if canonical:
            self.canonical.add(canonical)
            if len(path) < len(self.shortest.get(canonical, canonical + ".")):
                self.shortest[canonical] = path

    def is_resolvable(self, identifier: str) -> bool:
        """Return whether a site engine will be able to resolve given identifier.

        Known are the rendered paths (`::: path` + member paths below it), the canonical
        paths of the rendered objects and their import aliases (`pkg.Klass` for a
        rendered `pkg.sub.Klass`), but not members reached via an import alias
        (`pkg.Klass.method`): mkdocstrings only registers the aliases griffe knows.

        Args:
            identifier: The identifier of a reference
        """
        self._collect()
        if identifier in self.literal or identifier in self.canonical:
            return True
        if self.inventory is not None and identifier in self.inventory:
            return True
        if (obj := _resolve(identifier)) is None or _canonical(obj) not in self.canonical:
            return False
        parent = _resolve(identifier.rsplit(".", 1)[0])
        return parent is not None and _is_module(parent)

    def equivalent(self, identifier: str) -> str | None:
        """Return a resolvable identifier of the same object, if there is one.

        Args:
            identifier: The identifier of a reference
        """
        self._collect()
        if (obj := _resolve(identifier)) is None:
            return None
        canonical = _canonical(obj)
        if canonical is None:  # inherited member: the member of the defining class
            try:
                canonical = obj.final_target.path  # type: ignore[union-attr]
            except Exception:  # noqa: BLE001
                return None
        if canonical in self.canonical or canonical in self.literal:
            return self.shortest.get(canonical, canonical)
        return None

    def should_check(self, identifier: str) -> bool:
        """Return whether given identifier is a path of a package documented on the site."""
        self._collect()
        return bool(DOTTED_PATH_RE.fullmatch(identifier)) and (
            identifier.split(".", maxsplit=1)[0] in self.packages
        )

    def diagnose(self, identifier: str) -> tuple[str, str | None, bool]:
        """Return reason, suggestion and whether the suggestion is the same object.

        Args:
            identifier: The identifier of a reference
        """
        if (obj := _resolve(identifier)) is None:
            known = self.literal | self.canonical
            name = identifier.rsplit(".", 1)[-1]
            candidates = {k.rsplit(".", 1)[-1]: k for k in sorted(known, key=len, reverse=True)}
            matches = difflib.get_close_matches(name, list(candidates), n=1, cutoff=0.8)
            suggestion = candidates[matches[0]] if matches else None
            return f"`{identifier}` does not exist", suggestion, False
        equivalent = self.equivalent(identifier)
        if _canonical(obj) is None:
            owner = identifier.rsplit(".", 1)[0]
            return (
                f"inherited member, not rendered on the `{owner}` docs",
                equivalent,
                bool(equivalent),
            )
        if equivalent:
            return "member of an import alias, not registered by mkdocstrings", equivalent, True
        canonical = _canonical(obj)
        return f"no page documents `{canonical}` (no `::: {canonical}` block)", None, False

    def check(self, pages: Mapping[str, mk.MkPage] | None = None) -> list[RefIssue]:
        """Validate the references of all pages and of the rendered docstrings.

        Args:
            pages: Page path -> page node (to report the node that produced a reference)
        """
        self._collect()
        issues: list[RefIssue] = []
        for path, markdown in self.pages.items():
            seen: Counter[tuple[str, str]] = Counter()
            for lineno, title, identifier in find_references(markdown):
                occurrence = seen[title, identifier]
                seen[title, identifier] += 1
                if not self.should_check(identifier) or self.is_resolvable(identifier):
                    continue
                reason, suggestion, fixable = self.diagnose(identifier)
                origin, node = None, None
                if pages and (page := pages.get(path)) is not None:
                    origin, node = find_origin(page, title, identifier, occurrence)
                issue = RefIssue(
                    identifier=identifier,
                    title=title,
                    page=path,
                    line=lineno,
                    reason=reason,
                    origin=origin,
                    node=node,
                    suggestion=suggestion,
                    fixable=fixable,
                )
                issues.append(issue)
        issues.extend(self.check_docstrings())
        return issues

    def check_docstrings(self) -> list[RefIssue]:
        """Validate the references in the docstrings of the rendered objects."""
        self._collect()
        issues = []
        for canonical, (obj, page) in self.rendered.items():
            text, origin = _docstring(obj)
            for _, title, identifier in find_references(text):
                if not self.should_check(identifier) or self.is_resolvable(identifier):
                    continue
                reason, suggestion, _ = self.diagnose(identifier)
                issue = RefIssue(
                    identifier=identifier,
                    title=title,
                    page=page,
                    reason=reason,
                    origin=origin,
                    node=f"docstring of {canonical}",
                    suggestion=suggestion,
                )
                issues.append(issue)
        return issues


def _node_sources(node: mk.MkNode) -> Iterator[tuple[str, str | None, int]]:
    """Yield (source text, file, first line) of the raw input of given node."""
    import mknodes as mk

    match node:
        case mk.MkCommentedCode():  # before MkTemplate (subclass)
            code: Any = node._code
            if isinstance(code, str):
                yield code, None, 1
                return
            try:
                lines, start = inspect.getsourcelines(code)
                yield "".join(lines), inspect.getsourcefile(code), max(start, 1)
            except OSError, TypeError:
                pass
        case mk.MkTemplate():
            try:
                src, filename, _ = node.env.loader.get_source(node.env, node.template)  # type: ignore[union-attr]
            except Exception:  # noqa: BLE001
                return
            yield src, filename, 1
        case mk.MkText():
            yield node._text, None, 1


def _describe(node: mk.MkNode) -> str:
    import mknodes as mk

    match node:
        case mk.MkCommentedCode():
            name = getattr(node._code, "__qualname__", None)
            return f"MkCommentedCode({name})" if name else "MkCommentedCode"
        case mk.MkTemplate():
            return f"MkTemplate({node.template!r})"
    return type(node).__name__


def find_origin(
    page: mk.MkPage,
    title: str,
    identifier: str,
    occurrence: int = 0,
) -> tuple[str | None, str | None]:
    """Return (`file:line`, node description) of the node that wrote given reference.

    Searches the raw input of the page's nodes (templates, code, text). Nodes with a
    known source file win. If the reference occurs several times on the page,
    `occurrence` selects the matching occurrence in the sources.

    Args:
        page: The page containing the reference
        title: The title of the reference
        identifier: The identifier of the reference
        occurrence: Index of the occurrence of this reference on the page
    """
    needle = f"[{title}][{identifier}]"
    located: list[tuple[str, str]] = []
    unlocated: list[str] = []
    for _, node in page.iter_nodes():
        for text, filename, start in _node_sources(node):
            idx = text.find(needle)
            while idx != -1:
                if filename is None:
                    unlocated.append(_describe(node))
                else:
                    line = start + text.count("\n", 0, idx)
                    located.append((f"{_short_path(filename)}:{line}", _describe(node)))
                idx = text.find(needle, idx + len(needle))
    if located:
        return located[min(occurrence, len(located) - 1)]
    if unlocated:
        return None, unlocated[min(occurrence, len(unlocated) - 1)]
    return None, None


def check_output(
    output: BuildOutput,
    root: mk.MkNav | None = None,
    packages: Iterable[str] = (),
    inventory: Container[str] | None = None,
) -> list[RefIssue]:
    """Check the `[title][identifier]` references of all pages of a build.

    Args:
        output: The build output
        root: Root nav of the build (to report the nodes producing bad references)
        packages: Top-level packages to validate references for (in addition to the
                  ones rendered with `:::` blocks)
        inventory: Identifiers known from inventories
    """
    import mknodes as mk

    checker = RefChecker(packages=packages, inventory=inventory)
    for path, markdown in output.pages.items():
        checker.add_page(path, markdown)
    pages: dict[str, mk.MkPage] = {}
    if root is not None:
        for _, node in root.iter_nodes():
            if isinstance(node, mk.MkPage):
                path = pathlib.PurePath(node.resolved_file_path).as_posix()
                pages[path] = node
    return checker.check(pages)


def fix_references(output: BuildOutput, issues: Iterable[RefIssue]) -> list[RefIssue]:
    """Point fixable references of the pages to a path engines know (in place).

    For references to members of import aliases (`[x][pkg.Klass.method]` while
    `pkg.sub.Klass` is rendered) and to inherited members, the identifier gets replaced
    with the rendered path of the same object.

    Args:
        output: The build output whose pages get fixed
        issues: Issues found by `check_output`

    Returns:
        The issues which were fixed.
    """
    fixed = []
    for issue in issues:
        if not issue.fixable or not issue.suggestion or issue.line is None:
            continue
        if (markdown := output.pages.get(issue.page)) is None:
            continue
        lines = markdown.split("\n")
        old = f"[{issue.title}][{issue.identifier}]"
        line = lines[issue.line - 1]
        if old not in line:
            continue
        lines[issue.line - 1] = line.replace(old, f"[{issue.title}][{issue.suggestion}]", 1)
        output.pages[issue.page] = "\n".join(lines)
        fixed.append(issue)
    return fixed


ANCHOR_RE = re.compile(r'<a id="(?P<id>[A-Za-z_][\w.]*)"></a>')
HEADING_ANCHOR_RE = re.compile(r'^(?P<level>#{1,6}) +<a id="(?P<id>[A-Za-z_][\w.]*)"></a>')
CODE_TITLE_RE = re.compile(r"[\w.]+(?:\(\))?")


def find_anchors(output: BuildOutput) -> dict[str, tuple[str, str]]:
    """Return the objects documented with anchors (`<a id="dotted.path">`).

    Flavours without mkdocstrings render API docs with an anchor per object
    (see `rendering.apidocs`). Both the documented path and the canonical path of the
    object are mapped. If an object is documented several times, a heading wins over
    an object rendered without heading (top-level headings first), then the first one.

    Args:
        output: The build output

    Returns:
        Identifier -> (page path, anchor id).
    """
    ranked: dict[str, tuple[int, str, str]] = {}
    for path, markdown in output.pages.items():
        for _, line in iter_markdown_lines(markdown):
            heading = HEADING_ANCHOR_RE.match(line)
            for match in ANCHOR_RE.finditer(line):
                identifier = match["id"]
                rank = len(heading["level"]) if heading and heading["id"] == identifier else 9
                if identifier not in ranked or rank < ranked[identifier][0]:
                    ranked[identifier] = (rank, path, identifier)
    anchors = {k: (page, anchor) for k, (_, page, anchor) in ranked.items()}
    canonical: dict[str, tuple[str, str]] = {}
    for identifier, target in anchors.items():
        if (obj := _resolve(identifier)) is not None and (canon := _canonical(obj)):
            canonical.setdefault(canon, target)
    return canonical | anchors


def _page_url(source: str, target: str, anchor: str) -> str:
    if source == target:
        return f"#{anchor}"
    rel = posixpath.relpath(target, posixpath.dirname(source) or ".")
    return f"{urllib.parse.quote(rel)}#{anchor}"


class ReferenceLinker:
    """Turns `[title][dotted.path]` references into plain Markdown links.

    For Markdown read without a site engine (GitHub flavour): engines with autorefs
    resolve the references themselves.
    """

    def __init__(
        self,
        anchors: Mapping[str, tuple[str, str]],
        inventory: Mapping[str, Any] | None = None,
    ) -> None:
        """Constructor.

        Args:
            anchors: Identifier -> (page path, anchor id) of the documented objects
            inventory: Identifier -> URL (or inventory item) of objects documented
                       elsewhere
        """
        self.anchors = anchors
        self.inventory = inventory

    def target(self, identifier: str) -> tuple[str, str] | None:
        """Return (page, anchor) documenting given identifier.

        Objects without an own anchor (members not rendered, members of import
        aliases) link to the class documenting them.

        Args:
            identifier: The identifier of a reference
        """
        if target := self.anchors.get(identifier):
            return target
        obj = _resolve(identifier)
        if obj is not None and (canonical := _canonical(obj)) and canonical in self.anchors:
            return self.anchors[canonical]
        parent = identifier
        while "." in parent:
            parent = parent.rsplit(".", 1)[0]
            if (owner := _resolve(parent)) is None or _is_module(owner):
                return None
            if target := self.target(parent):
                return target
        return None

    def url(self, identifier: str, page: str) -> str | None:
        """Return the URL for given identifier, relative to given page (None: unknown).

        Args:
            identifier: The identifier of a reference
            page: Path of the page containing the reference
        """
        if target := self.target(identifier):
            return _page_url(page, *target)
        if self.inventory is not None and identifier in self.inventory:
            item = self.inventory[identifier]
            return str(getattr(item, "uri", item))
        return None

    def link(self, markdown: str, page: str) -> str:
        """Replace the dotted-path references of given page Markdown.

        Unknown objects become code (or plain text, for prose titles). References inside
        code and references to link definitions of the page stay untouched.

        Args:
            markdown: Markdown of the page
            page: Path of the page (relative to the docs root)
        """
        refs = {lineno for lineno, _, _ in find_references(markdown)}
        if not refs:
            return markdown
        lines = markdown.split("\n")
        code_free = dict(iter_markdown_lines(markdown))
        labels = {m[1].lower() for line in code_free.values() if (m := LABEL_DEF_RE.match(line))}
        for lineno in refs:
            line, blanked = lines[lineno - 1], code_free[lineno]
            parts: list[str] = []
            pos = 0
            for match in REF_RE.finditer(blanked):
                title = line[match.start(1) : match.end(1)]
                identifier = line[match.start(2) : match.end(2)] or title
                if identifier.lower() in labels or not DOTTED_PATH_RE.fullmatch(identifier):
                    continue
                parts.append(line[pos : match.start()])
                if url := self.url(identifier, page):
                    parts.append(f"[{title}]({url})")
                elif CODE_TITLE_RE.fullmatch(title):
                    parts.append(f"`{title}`")
                else:
                    parts.append(title)
                pos = match.end()
            parts.append(line[pos:])
            lines[lineno - 1] = "".join(parts)
        return "\n".join(lines)


def link_references(
    output: BuildOutput,
    inventory: Mapping[str, Any] | None = None,
) -> None:
    """Turn the `[title][dotted.path]` references of all pages into links (in place).

    References to objects documented on the site link to their anchor, others to
    their inventory URL; unknown objects become code.

    Args:
        output: The build output
        inventory: Identifier -> URL (or inventory item) of objects documented elsewhere
    """
    linker = ReferenceLinker(find_anchors(output), inventory)
    for path, markdown in output.pages.items():
        output.pages[path] = linker.link(markdown, path)
