import pytest

import mknodes as mk
from mknodes.build import DocBuilder, fencecheck


CODE_FENCE = "``` {.python  title='x' linenums='4'}"


def test_valid_fences():
    md = f"""{CODE_FENCE}
a = 1
```

```python
b = 2
```

    ```` {{.markdown }}
    ```md
    x
    ```
    ````

```rust,ignore
fn main() {{}}
```

~~~
c
~~~

```{{code-block}} python
:caption: MyST directive
d = 1
```

Inline ```code``` is fine.
"""
    assert fencecheck.check_fences(md) == []


def test_mangled_attribute_list():
    md = "``` <.python  title='x' linenums='4'>\na = 1\n```\n"
    (problem,) = fencecheck.check_fences(md)
    assert problem.startswith("line 1: unrecognised code fence")


def test_unclosed_fence():
    md = "````\n```\ncode\n```\n"
    assert fencecheck.check_fences(md) == ["line 1: code fence '````' never closed"]


def build_tree() -> mk.MkNav:
    root = mk.MkNav()
    other = root.add_page("Other")
    other += "Target page."
    page = root.add_page("Code")
    page += "See [MkCode][mknodes.MkCode], [Other](other.md) and <https://example.org>."
    page += mk.MkCode("a = {'x': 1}", language="python", title="x", linenums=4)
    page += "After the code: [MkText][mknodes.MkText] and `{{ 1 + 1 }}`."
    page += mk.MkCode("```md\ninner\n```", language="markdown")
    return root


@pytest.mark.parametrize("flavor", ["material", "github"])
def test_code_block_with_attributes_survives_build(flavor: str):
    output = DocBuilder(flavor=flavor).build(build_tree())
    md = output.pages["code.md"]
    assert fencecheck.check_fences(md) == []
    assert "<.python" not in md
    if flavor == "material":
        assert CODE_FENCE in md
        assert "```` {.markdown }\n```md\ninner\n```\n````" in md
    else:
        assert "**x**\n\n```python\na = {'x': 1}\n```" in md
        assert "````markdown\n```md\ninner\n```\n````" in md
    # Jinja got rendered around the block, the block itself stays intact.
    assert "a = {'x': 1}" in md
    assert "`2`" in md


def _commented(page: mk.MkPage) -> None:
    # Result: {{ 1 + 1 }}
    page += mk.MkCode("x = {'a': 1}", language="python", title="x", linenums=4)


@pytest.mark.parametrize("flavor", ["material", "github"])
def test_commented_code_renders_jinja_in_comments_only(flavor: str):
    root = mk.MkNav()
    page = root.add_page("Tour")
    page.metadata.render_macros = False
    page += mk.MkCommentedCode(_commented, style="text", render_comments=True)
    page += mk.MkCode.for_object(_commented)
    md = (DocBuilder(flavor=flavor).build(root)).pages["tour.md"]
    assert "Result: 2" in md
    assert "# Result: {{ 1 + 1 }}" in md  # the raw source stays as it is
    assert fencecheck.check_fences(md) == []
