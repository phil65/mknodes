from __future__ import annotations

from jinjarope import inspectfilters
import pytest

import mknodes as mk


def example_instances():
    """Iterates over example instances of MkNode subclasses.
    
    This method generates example instances for all subclasses of MkNode that have
    a defined nodefile. It creates a MkPage context and uses it to iterate through
    the example instances of each applicable subclass.
    
    Args:
        None
    
    Returns:
        Iterator[Any]: An iterator yielding example instances of MkNode subclasses.
    
    Raises:
        None
    """
    page = mk.MkPage.with_context()
    for cls in inspectfilters.list_subclasses(mk.MkNode):
        if cls.nodefile:
            yield from cls.nodefile.iter_example_instances(page)


@pytest.mark.parametrize("node", example_instances(), ids=lambda x: x.__class__.__name__)
def test_if_example_can_get_rendered(node):
    """Tests if examples in a node can be rendered.
    
    Args:
        node: The node object containing examples to be tested.
    
    Returns:
        None
    
    Raises:
        Any exceptions that may occur during rendering or evaluation of examples.
    """
    if nodefile := node.nodefile:
        for v in nodefile.examples.values():
            if "jinja" in v:
                node.env.render_string(v["jinja"])
            if "python" in v:
                node.env.evaluate(v["python"])


@pytest.mark.parametrize("node", example_instances(), ids=lambda x: x.__class__.__name__)
def test_if_template_output_equals_code_output(node: mk.MkNode):
    """Test if template output equals code output
    
    Args:
        node (mk.MkNode): The MkNode object to be tested
    
    Returns:
        None
    
    Raises:
        AssertionError: If the rendered template output does not match the markdown output of the node
    """
    if nodefile := node.nodefile:
        for k, v in nodefile.output.items():
            if k not in {"markdown", "html"}:
                continue
            result = node.env.render_string(v["template"], dict(node=node))
            assert result == node._to_markdown()
            break


if __name__ == "__main__":
    pytest.main([__file__])
