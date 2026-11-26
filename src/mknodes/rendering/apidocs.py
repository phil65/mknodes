"""API docs as plain Markdown, rendered from Griffe objects.

For flavours whose engine has no mkdocstrings (`::: dotted.path` blocks). Supports the
common mkdocstrings options: `heading_level`, `show_root_heading`, `show_root_full_path`,
`show_signature`, `show_bases`, `members`, `members_order`, `filters`, `inherited_members`,
`show_submodules`, `show_if_no_docstring`, `merge_init_into_class`,
`show_docstring_description`.

Every rendered object gets an HTML anchor (`<a id="dotted.path"></a>`, in its heading),
so references to it can be linked.
"""

import re
from typing import TYPE_CHECKING, Any

import griffe

from mknodes.utils import log


if TYPE_CHECKING:
    from collections.abc import Iterator


logger = log.get_logger(__name__)

DEFAULT_FILTERS = ["!^_[^_]"]
KIND_ORDER = {
    griffe.Kind.ATTRIBUTE: 0,
    griffe.Kind.CLASS: 1,
    griffe.Kind.FUNCTION: 2,
    griffe.Kind.MODULE: 3,
}


def anchor(path: str) -> str:
    """Return the HTML anchor marking where the object with given path is documented.

    `[title][dotted.path]` references get linked to these anchors
    (see `refcheck.link_references`).
    """
    return f'<a id="{path}"></a>'


def render(obj: griffe.Object | griffe.Alias, options: dict[str, Any] | None = None) -> str:
    """Render API docs for given Griffe object (like mkdocstrings' `::: path`)."""
    opts = options or {}
    level = opts.get("heading_level") or 2
    return _Renderer(opts).render(obj, level, root=True).strip() + "\n"


class _Renderer:
    def __init__(self, options: dict[str, Any]) -> None:
        self.opts = options
        self.filters = [
            (f.startswith("!"), re.compile(f.removeprefix("!")))
            for f in options.get("filters") or DEFAULT_FILTERS
        ]

    def render(self, obj: griffe.Object | griffe.Alias, level: int, *, root: bool = False) -> str:
        parts: list[str] = []
        if not root or self.opts.get("show_root_heading"):
            parts.append(self.heading(obj, level, root=root))
            level += 1
        else:
            parts.append(anchor(obj.path))
        if self.opts.get("show_signature", True) and (sig := self.signature(obj)):
            parts.append(f"```python\n{sig}\n```")
        if self.opts.get("show_docstring_description", True):
            parts.extend(self.docstring(obj))
        parts.extend(self.render(member, level) for member in self.members(obj))
        return "\n\n".join(p for p in parts if p)

    def heading(self, obj: griffe.Object | griffe.Alias, level: int, *, root: bool) -> str:
        full = root and self.opts.get("show_root_full_path", True)
        name = obj.path if full else obj.name
        return f"{'#' * min(level, 6)} {anchor(obj.path)}`{name}`"

    # --- signatures ---

    def signature(self, obj: griffe.Object | griffe.Alias) -> str | None:
        match obj.kind:
            case griffe.Kind.FUNCTION:
                assert isinstance(obj, griffe.Function | griffe.Alias)
                prefix = "async def" if "async" in obj.labels else "def"
                params = _params(obj.parameters)
                returns = f" -> {obj.returns}" if obj.returns else ""
                return f"{prefix} {obj.name}({params}){returns}"
            case griffe.Kind.CLASS:
                assert isinstance(obj, griffe.Class | griffe.Alias)
                bases = ", ".join(str(b) for b in obj.bases)
                if self.opts.get("merge_init_into_class") and "__init__" in obj.members:
                    init = obj.members["__init__"]
                    assert isinstance(init, griffe.Function | griffe.Alias)
                    return f"{obj.name}({_params(init.parameters)})"
                if not self.opts.get("show_bases", True):
                    bases = ""
                return f"class {obj.name}({bases})" if bases else f"class {obj.name}"
            case griffe.Kind.ATTRIBUTE:
                assert isinstance(obj, griffe.Attribute | griffe.Alias)
                annotation = f": {obj.annotation}" if obj.annotation else ""
                value = f" = {obj.value}" if obj.value is not None else ""
                return f"{obj.name}{annotation}{value}"
        return None

    # --- docstrings ---

    def docstring(self, obj: griffe.Object | griffe.Alias) -> Iterator[str]:
        if not obj.docstring:
            return
        for section in obj.docstring.parsed:
            if text := _section(section):
                yield text

    # --- members ---

    def members(self, obj: griffe.Object | griffe.Alias) -> list[griffe.Object | griffe.Alias]:
        if obj.kind not in {griffe.Kind.MODULE, griffe.Kind.CLASS}:
            return []
        members = dict(obj.members)
        if obj.kind is griffe.Kind.CLASS and self.opts.get("inherited_members"):
            members = {**obj.inherited_members, **members}
        wanted = self.opts.get("members")
        if wanted is False:
            return []
        result = []
        for name, member in members.items():
            if isinstance(wanted, list):
                if name not in wanted:
                    continue
            elif not self._is_documented(name, member):
                continue
            result.append(member)
        if self.opts.get("members_order") == "source":
            result.sort(key=lambda m: (KIND_ORDER.get(m.kind, 9), m.lineno or 0))
        else:
            result.sort(key=lambda m: (KIND_ORDER.get(m.kind, 9), m.name))
        return result

    def _is_documented(self, name: str, member: griffe.Object | griffe.Alias) -> bool:
        try:
            return self._check_documented(name, member)
        except (griffe.AliasResolutionError, griffe.CyclicAliasError) as e:
            # e.g. imports shadowing a class (`from pkg import X` in an `if __name__` block)
            logger.debug("Skipping unresolvable member %s: %s", member.path, e)
            return False

    def _check_documented(self, name: str, member: griffe.Object | griffe.Alias) -> bool:
        excluded = (
            (member.is_alias and not member.is_exported)  # imports
            or (member.is_module and not self.opts.get("show_submodules"))
            or (name == "__init__" and self.opts.get("merge_init_into_class"))
            or (not member.is_alias and not member.is_public)  # respects __all__
            or not self._passes_filters(name)
        )
        if excluded:
            return False
        has_docs = bool(member.docstring) or member.has_docstrings
        return has_docs or bool(self.opts.get("show_if_no_docstring"))

    def _passes_filters(self, name: str) -> bool:
        keep = True
        for negate, pattern in self.filters:
            if pattern.search(name):
                keep = not negate
            elif not negate:
                keep = False
        return keep


def _params(parameters: griffe.Parameters) -> str:
    parts = []
    seen_kw_only = False
    for param in parameters:
        if param.name in {"self", "cls"}:
            continue
        text = param.name
        match param.kind:
            case griffe.ParameterKind.var_positional:
                text = f"*{text}"
                seen_kw_only = True
            case griffe.ParameterKind.var_keyword:
                text = f"**{text}"
            case griffe.ParameterKind.keyword_only if not seen_kw_only:
                parts.append("*")
                seen_kw_only = True
        if param.annotation:
            text += f": {param.annotation}"
        is_variadic = param.kind in {
            griffe.ParameterKind.var_positional,
            griffe.ParameterKind.var_keyword,
        }
        if param.default is not None and not is_variadic:
            text += f" = {param.default}" if param.annotation else f"={param.default}"
        parts.append(text)
    return ", ".join(parts)


def _cell(text: Any) -> str:
    """Make text usable inside a table cell."""
    return str(text or "").strip().replace("|", "\\|").replace("\n", "<br>")


def _section(section: griffe.DocstringSection) -> str | None:  # noqa: PLR0911
    kind = griffe.DocstringSectionKind
    match section.kind:
        case kind.text:
            return str(section.value).strip()
        case kind.parameters | kind.other_parameters | kind.attributes:
            title = section.title or section.kind.value.replace("_", " ").capitalize()
            rows = [
                f"| `{p.name}` | {_cell(p.annotation and f'`{p.annotation}`')} "
                f"| {_cell(p.description)} | {_cell(getattr(p, 'default', None))} |"
                for p in section.value
            ]
            header = "| Name | Type | Description | Default |\n| --- | --- | --- | --- |"
            return f"**{title}:**\n\n{header}\n" + "\n".join(rows)
        case kind.returns | kind.yields | kind.receives | kind.raises | kind.warns:
            title = section.title or section.kind.value.capitalize()
            rows = [
                f"| {_cell(i.annotation and f'`{i.annotation}`')} | {_cell(i.description)} |"
                for i in section.value
            ]
            return f"**{title}:**\n\n| Type | Description |\n| --- | --- |\n" + "\n".join(rows)
        case kind.examples:
            blocks = []
            for example_kind, text in section.value:
                is_code = example_kind == griffe.DocstringSectionKind.examples
                blocks.append(f"```pycon\n{text}\n```" if is_code else text)
            return "**Examples:**\n\n" + "\n\n".join(blocks)
        case kind.admonition:
            value = section.value
            return f"**{section.title or value.annotation}:**\n\n{value.description}"
        case kind.deprecated:
            value = section.value
            return f"**Deprecated since {value.version}:** {value.description}"
    return None
