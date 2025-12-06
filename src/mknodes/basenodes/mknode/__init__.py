from __future__ import annotations

import copy
import functools
import re
from typing import TYPE_CHECKING, Any, Self

from mknodes.basenodes import processors
from mknodes.data import treestyles
from mknodes.info import contexts, nodefile
from mknodes.jinja import nodeenvironment
from mknodes.nodemods.modmanager import ModManager
from mknodes.utils import icons, log, mdconverter, reprhelpers, resources, coroutines


if TYPE_CHECKING:
    from collections.abc import Callable, Iterable, Iterator
    import types

    from mknodes.data import datatypes
    import mknodes as mk


logger = log.get_logger(__name__)
HEADER_REGEX = re.compile(r"^(#{1,6}) (.*)")
fallback_ctx = contexts.ProjectContext()


class IllegalArgumentError(ValueError):
    def __init__(self, node: mk.MkNode, kwargs: Any) -> None:
        msg = f"Invalid keyword arguments for {type(node)!r}: {kwargs}"
        super().__init__(msg)


class MkNode:
    """Base class for everything which can be expressed as Markup.

    This class combines tree node functionality with markdown generation.
    Starting from the root nav (aka Docs) down to nested Markup blocks,
    the whole project can be represented by one tree.

    MkNode is the base class for all nodes. We dont instanciate it directly.
    All subclasses carry an MkAnnotations node (except the MkAnnotations node itself)
    They can also pass an `indent` as well as a `shift_header_levels` keyword argument
    in order to modify the resulting markdown.
    """

    # METADATA (should be set by subclasses)

    ICON = "material/puzzle-outline"
    ATTR_LIST_SEPARATOR = " "
    REQUIRED_EXTENSIONS: list[resources.Extension] = []
    REQUIRED_PLUGINS: list[resources.Plugin] = []
    STATUS: datatypes.PageStatusStr | str | None = None
    CSS: list[resources.CSSFile | resources.CSSText] = []
    JS_FILES: list[resources.JSFile | resources.JSText] = []

    _name_registry: dict[str, MkNode] = dict()

    def __init__(
        self,
        *,
        header: str = "",
        indent: str = "",
        name: str | None = None,
        shift_header_levels: int = 0,
        variables: dict[str, Any] | None = None,
        context: contexts.ProjectContext | None = None,
        parent: MkNode | None = None,
        **_kwargs: Any,
    ) -> None:
        """Constructor.

        Args:
            header: Optional header for contained Markup
            indent: Indentation of given Markup (unused ATM)
            name: An optional unique identifier (allows getting node via MkNode.get_node)
            shift_header_levels: Regex-based header level shifting (adds/removes #-chars)
            variables: Variables to use for rendering
            context: Context this Nav is connected to.
            parent: Parent for building the tree
        """
        # Tree node initialization
        self._parent: MkNode | None = parent
        self._children: list[MkNode] = []

        if _kwargs:
            raise IllegalArgumentError(self, _kwargs)
        self.header = header
        self.indent = indent
        self.shift_header_levels = shift_header_levels
        self._files: dict[str, str | bytes] = {}
        self.mods = ModManager()
        self._ctx = context
        self._node_name = name
        self.variables = variables or {}
        if name is not None:
            self._name_registry[name] = self
        self.__post_init__()

    def __post_init__(self) -> None:
        pass

    # -------------------------------------------------------------------------
    # Tree node methods
    # -------------------------------------------------------------------------

    def get_children(self) -> list[MkNode]:
        """Return the list of children nodes."""
        return self._children

    def __repr__(self) -> str:
        return reprhelpers.get_nondefault_repr(self)

    def __iter__(self) -> Iterator[MkNode]:
        yield from self.get_children()

    @property
    def parent(self) -> MkNode | None:
        """The parent node of this node."""
        return self._parent

    @parent.setter
    def parent(self, value: MkNode | None) -> None:
        self._parent = value

    def __copy__(self, **kwargs: Any) -> Self:
        """Shallow copy self."""
        obj = type(self).__new__(self.__class__)
        obj.__dict__.update(self.__dict__)
        obj.__dict__.update(kwargs)
        return obj

    def __deepcopy__(self, memo: Any):
        cls = self.__class__
        result = cls.__new__(cls)
        memo[id(self)] = result
        for k, v in self.__dict__.items():
            setattr(result, k, copy.deepcopy(v, memo))
        return result

    @property
    def ancestors(self) -> Iterable[MkNode]:
        """Get iterator to yield all ancestors of self, does not include self."""
        node = self._parent
        while node is not None:
            yield node
            node = node._parent

    @property
    def descendants(self) -> Iterable[MkNode]:
        """Get iterator to yield all descendants of self, does not include self."""
        yield from self._preorder_iter(filter_condition=lambda _node: _node != self)

    def is_descendant_of(self, kls: type | types.UnionType) -> bool:
        """Returns True if any ancestor is of given type.

        Args:
            kls: The class (union) the check the ancestors for
        """
        return any(isinstance(i, kls) for i in self.ancestors)

    @property
    def siblings(self) -> Iterable[MkNode]:
        """Get siblings of self."""
        if self._parent is None:
            return ()
        return tuple(child for child in self._parent.get_children() if child is not self)

    @property
    def left_sibling(self) -> MkNode | None:
        """Get sibling left of self."""
        if not self._parent:
            return None
        children = self._parent.get_children()
        if child_idx := children.index(self):
            return children[child_idx - 1]
        return None

    @property
    def right_sibling(self) -> MkNode | None:
        """Get sibling right of self."""
        if not self._parent:
            return None
        children = self._parent.get_children()
        child_idx = children.index(self)
        if child_idx + 1 < len(children):
            return children[child_idx + 1]
        return None

    @property
    def node_path(self) -> list[MkNode]:
        """Get list of nodes starting from root."""
        if self._parent is None:
            return [self]
        path = list(self._parent.node_path)
        return [*path, self]

    @property
    def is_root(self) -> bool:
        """Get indicator if self is root node."""
        return self._parent is None

    @property
    def is_leaf(self) -> bool:
        """Get indicator if self is leaf node."""
        return not list(self.get_children())

    @property
    def root(self) -> MkNode:
        """Get root node of tree."""
        return self if self._parent is None else self._parent.root

    @property
    def depth(self) -> int:
        """Get depth of self, indexing starts from 1."""
        return 1 if self._parent is None else self._parent.depth + 1

    @property
    def max_depth(self) -> int:
        """Get maximum depth from root to leaf node."""
        return max(
            [self.root.depth] + [node.depth for node in list(self.root.descendants)],
        )

    def row(self) -> int:  # sourcery skip: assign-if-exp
        """Return the position of this node inside the parent's children list."""
        if self._parent:
            return self._parent.get_children().index(self)
        return 0

    def pformat(self, indent: int = 0, max_depth: int | None = None):
        lines = [i * f"    {child!r}" for i, child in self.iter_nodes(indent, max_depth)]
        return "\n".join(lines)

    def iter_nodes(
        self, indent: int = 0, max_depth: int | None = None
    ) -> Iterator[tuple[int, MkNode]]:
        """Iterate over all nodes, including self and children.

        Yields current-depth-node tuples.

        Args:
            indent: The start "level". The first element of the returned tuple will be
                    relative to this
            max_depth: The max depth to iterate
        """
        if max_depth is not None and indent > max_depth:
            return
        yield indent, self
        for child_item in self.get_children():
            yield from child_item.iter_nodes(indent + 1)

    def get_tree_repr(
        self,
        max_depth: int | None = None,
        style: treestyles.TreeStyleStr | tuple[str, str, str, str] | None = None,
        detailed: bool = True,
    ) -> str:
        def formatter(x: object) -> str:
            return repr(x) if detailed else x.__class__.__name__

        lines = [
            f"{pre_str}{fill_str}{formatter(node)}"
            for pre_str, fill_str, node in self._yield_tree(
                max_depth=max_depth,
                style=style or "ascii",
            )
        ]
        return self.__class__.__name__ + "\n" + "\n".join(lines[1:])

    def _yield_tree(
        self,
        max_depth: int | None = None,
        style: treestyles.TreeStyleStr | tuple[str, ...] = "const",
    ) -> Iterable[tuple[str, str, MkNode]]:
        """Yield a tuple for prettyprinting the tree.

        Tuple consists of two strings to be used as a prefix, and the node itself.

        Args:
            max_depth: The maxium depth of nodes to yield
            style: The prefix style.
        """
        if isinstance(style, tuple):
            custom_style: list[str] = list(style)
            parent_last, filename_middle, filename_last = custom_style
            gap_str = " " * len(parent_last)
        else:
            style_obj = treestyles.STYLES[style]
            parent_last = style_obj.parent_last
            filename_middle = style_obj.filename_middle
            filename_last = style_obj.filename_last
            gap_str = style_obj.parent_middle
        unclosed_depth: set[int] = set()
        initial_depth = self.depth
        for node in self._preorder_iter(max_depth=max_depth):
            pre_str = ""
            fill_str = ""
            if not node.is_root:
                node_depth = node.depth - initial_depth

                # Get fill_str (filename_middle or filename_last)
                if node.right_sibling:
                    unclosed_depth.add(node_depth)
                    fill_str = filename_middle
                else:
                    if node_depth in unclosed_depth:
                        unclosed_depth.remove(node_depth)
                    fill_str = filename_last

                pre_str = "".join(
                    parent_last if depth in unclosed_depth else gap_str
                    for depth in range(1, node_depth)
                )
            yield pre_str, fill_str, node

    def _preorder_iter(
        self,
        filter_condition: Callable[[MkNode], bool] | None = None,
        stop_condition: Callable[[MkNode], bool] | None = None,
        max_depth: int | None = None,
    ) -> Iterator[MkNode]:
        """Iterate through all children of a tree.

        It is topologically sorted because a parent node is processed before its child
        nodes.

        Args:
            filter_condition: function that takes in node as argument
            stop_condition: function that takes in node as argument
            max_depth: maximum depth of iteration, based on `depth` attribute
        """
        if (not max_depth or self.depth <= max_depth) and (
            not stop_condition or not stop_condition(self)
        ):
            if not filter_condition or filter_condition(self):
                yield self
            for child in self.get_children():
                yield from child._preorder_iter(filter_condition, stop_condition, max_depth)

    # -------------------------------------------------------------------------
    # MkNode specific methods
    # -------------------------------------------------------------------------

    @functools.cached_property
    def annotations(self):
        import mknodes as mk

        return mk.MkAnnotations(parent=self)

    @functools.cached_property
    def env(self):
        """The node jinja environment.

        The environment has additional loaders for the class file path
        as well as the resolved parent nav file path.
        """
        return nodeenvironment.NodeEnvironment(self)

    def __str__(self) -> str:
        return coroutines.run_sync(self.to_markdown())

    def __hash__(self):
        return hash(coroutines.run_sync(self.to_markdown()))

    def __eq__(self, other: object):
        if type(other) is not type(self):
            return False
        dct_1 = self.__dict__.copy()
        dct_2 = other.__dict__.copy()
        for attr in ["_parent", "env"]:  # , "_annotations"]
            if attr in dct_1:
                dct_1.pop(attr)
            if attr in dct_2:
                dct_2.pop(attr)
        return dct_1 == dct_2

    @property
    def ctx(self) -> contexts.ProjectContext:
        """The tree context.

        Will return the attached context or the closest context from parents.
        If no context is found, return an "empty" ProjectContext.
        """
        if self._ctx:
            return self._ctx
        for ancestor in self.ancestors:
            if ancestor._ctx:
                return ancestor._ctx
        return fallback_ctx

    @property
    def parent_navs(self) -> list[mk.MkNav]:
        """Return a list of parent MkNavs, ordered from root to leaf."""
        import mknodes as mk

        navs = [i for i in self.ancestors if isinstance(i, mk.MkNav)]
        return list(reversed(navs))

    @property
    def parent_page(self) -> mk.MkPage | None:
        """Return the page which contains this node if existing."""
        import mknodes as mk

        return next((i for i in self.ancestors if isinstance(i, mk.MkPage)), None)

    @classmethod
    def get_nodefile(cls) -> nodefile.NodeFile | None:
        """Return the NodeFile if existing."""
        return nodefile.get_nodefile(cls)  # type: ignore[arg-type]

    def to_child_node(self, other: str | list[Any] | mk.MkNode | None):  # type: ignore[return]
        """Convert given nodes / strings to child nodes.

        Either converts text to an MkNode sets parent of node to self.

        Args:
            other: The node / string to convert to a child node.
        """
        import mknodes as mk

        match other:
            case str() if (match := HEADER_REGEX.match(other)) and "\n" not in other:
                return mk.MkHeader(match[2], level=len(match[1]), parent=self)
            case str():
                return mk.MkText(other, parent=self)
            case list():
                return mk.MkContainer(other, parent=self)
            case mk.MkNode():
                other.parent = self
                return other
            case _:
                raise TypeError(other)

    @classmethod
    def get_node(cls, name: str) -> MkNode:
        """Get a node from name registry."""
        return cls._name_registry[name]

    async def get_toc(self):
        from mknodes.pages import toc

        return toc.get_toc(await self.to_markdown())

    async def to_md_unprocessed(self) -> str:
        """Return raw markdown for this node. Override in subclasses for custom markdown."""
        return ""

    async def get_content(self) -> resources.NodeContent:
        """Return markdown and resources for this node in a single pass.

        Override this method in subclasses to compute both markdown and resources
        together when they share expensive computation.

        Default implementation calls legacy methods `to_md_unprocessed()` and
        `_build_node_resources()` for backward compatibility.
        """
        return resources.NodeContent(
            markdown=await self.to_md_unprocessed(),
            resources=await self._build_node_resources(),
        )

    async def _build_node_resources(self) -> resources.Resources:
        """Build resources from class attributes and mods. Internal helper."""
        extension: dict[str, dict[str, Any]] = {
            k.extension_name: dict(k) for k in self.REQUIRED_EXTENSIONS
        }

        mod_resources = self.mods.get_resources()
        css_resources: list[resources.CSSType] = []
        for css in self.CSS + mod_resources.css:
            if isinstance(css, resources.CSSFile) and css.is_local():
                text = await self.env.render_template_async(css.link)
                css_resource = resources.CSSText(text, css.link)
                css_resources.append(css_resource)
            else:
                css_resources.append(css)
        js_resources: list[resources.JSType] = []
        for js_file in self.JS_FILES + mod_resources.js:
            if isinstance(js_file, resources.JSFile) and js_file.is_local():
                text = await self.env.render_template_async(js_file.link)
                js_resource = resources.JSText(
                    text,
                    js_file.link,
                    defer=js_file.defer,
                    async_=js_file.async_,
                    crossorigin=js_file.crossorigin,
                    typ=js_file.typ,
                    is_library=js_file.is_library,
                )
                js_resources.append(js_resource)
            else:
                js_resources.append(js_file)
        return resources.Resources(
            js=js_resources,
            markdown_extensions=extension,
            plugins=self.REQUIRED_PLUGINS,
            css=css_resources,
        )

    async def to_markdown(self) -> str:
        """Outputs markdown for self and all children."""
        text = await self.to_md_unprocessed()
        for proc in self.get_processors():
            text = proc.run(text)
        return text

    def get_processors(self) -> list[processors.TextProcessor]:
        """Return list of processors used to created markdown."""
        return [
            processors.ShiftHeaderLevelProcessor(self.shift_header_levels),
            processors.IndentationProcessor(self.indent),
            processors.AppendCssClassesProcessor(self),
            processors.PrependHeaderProcessor(self.header),
            processors.AnnotationProcessor(self),
        ]

    def attach_annotations(self, text: str) -> str:
        """Attach annotations block to given markdown.

        Can be reimplemented if non-default annotations are needed.

        Args:
            text: Markdown to annote
        """
        return self.annotations.annotate_text(text) if self.annotations else text

    def attach_css_classes(self, text: str) -> str:
        """Attach CSS classes to given markdown in attr-list style.

        Can be reimplemented if non-default behavior is needed.
        Default behavior is appending the css class snippet with a space
        as separator.

        Args:
            text: Markdown to annote
        """
        if not self.mods.css_classes:
            return text
        classes = " ".join(f".{kls_name}" for kls_name in self.mods.css_classes)
        text += f"{self.ATTR_LIST_SEPARATOR}{{: {classes}}}"
        return text

    @property
    def resolved_parts(self) -> tuple[str, ...]:
        """Return a tuple containing all section names."""
        import mknodes as mk

        parts = [nav.title for nav in self.parent_navs if nav.title]
        if isinstance(self, mk.MkNav) and self.title:
            parts.append(self.title)
        return tuple(parts)

    @property
    def files(self) -> dict[str, str | bytes]:
        """Return a dict containing the virtual files attached to this tree element.

        This can be overridden by nodes if they want files to be included dynamically.
        For static files, use `add_file`.
        """
        return self._files

    def add_file(self, filename: str, data: str | bytes) -> None:
        """Add a static file as data to this node.

        Args:
            filename: Filename of the file to add
            data: Data of the file
        """
        self._files[filename] = data

    def add_css_class(self, class_name: str) -> None:
        """Wrap node markdown with given css class.

        Args:
            class_name: CSS class to wrap the node with
        """
        self.mods._css_classes.append(class_name)

    async def get_node_resources(self) -> resources.Resources:
        """Return the resources specific for this node.

        Default implementation calls `_build_node_resources()`. Override
        `get_content()` if you need to compute markdown and resources together.
        """
        return await self._build_node_resources()

    async def get_resources(self) -> resources.Resources:
        """Return the "final" resources object."""
        nodes = [*list(self.descendants), self]
        extensions: dict[str, dict[str, Any]] = {
            "attr_list": {},
            "md_in_html": {},
            "pymdownx.emoji": {
                "emoji_index": icons.twemoji,
                "emoji_generator": icons.to_svg,
            },
            "pymdownx.magiclink": dict(
                repo_url_shorthand=True,
                user=self.ctx.metadata.repository_username,
                repo=self.ctx.metadata.repository_name,
            ),
        }

        req = resources.Resources(markdown_extensions=extensions)
        for node in nodes:
            node_req = await node.get_node_resources()
            req.merge(node_req)
        return req

    @classmethod
    def with_context(
        cls,
        *args: Any,
        repo_url: str | None = None,
        base_url: str = "",
        **kwargs: Any,
    ) -> Self:
        """Same as the Ctor, but auto-adds a context for the repo url (or the cwd)."""
        ctx = contexts.ProjectContext.for_config(repo_url=repo_url, base_url=base_url)
        return cls(*args, **kwargs, context=ctx)

    async def to_html(self) -> str:
        """Convert node to HTML using the resources from node + children."""
        md = await self.to_markdown()
        reqs = await self.get_resources()
        configs = reqs.markdown_extensions
        exts = list(configs.keys())
        converter = mdconverter.MdConverter(extensions=exts, extension_configs=configs)
        return converter.convert(md)
