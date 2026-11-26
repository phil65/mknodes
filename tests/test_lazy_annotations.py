"""Runtime introspection of annotations naming TYPE_CHECKING-only imports (PEP 649)."""

import annotationlib
import inspect

import pytest

import mknodes as mk
from mknodes.build import builder
from mknodes.build.output import BuildOutput
from mknodes.utils import reprhelpers
from mknodes.utils.resources import Resources


def test_node_init_annotations_are_lazy() -> None:
    # MkAdmonition's annotations use names only imported under TYPE_CHECKING
    with pytest.raises(NameError):
        inspect.signature(mk.MkAdmonition.__init__)


def test_get_repr_with_type_checking_only_annotations() -> None:
    node = mk.MkAdmonition("text", typ="warning")
    assert reprhelpers.get_nondefault_repr(node).startswith("MkAdmonition(")


def test_jinja_node_error_message_with_type_checking_only_annotations() -> None:
    page = mk.MkPage()
    page.env.render_string(r"{{ 'x' | MkAdmonition(not_a_param=1) }}")
    node = page.env.rendered_nodes[-1]
    assert isinstance(node, mk.MkText)
    assert "Signature: MkAdmonition(content" in str(node._text)


def test_logfire_instrumented_signature_evaluates() -> None:
    inspect.signature(builder.DocBuilder._render_page)


def test_build_output_annotations_not_shadowed_by_property() -> None:
    anns = annotationlib.get_annotations(BuildOutput, format=annotationlib.Format.FORWARDREF)
    assert anns["page_resources"] == dict[str, Resources]
