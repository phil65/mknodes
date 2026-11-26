# Markdown-Exec

````python
import mknodes as mk
from mknodes import paths

INFO = """MkNodes also works great in combination with Markdown-exec! You can embed small
snippets into your existing documentation."""

header = mk.MkHeader("Markdown for this page")
path = paths.TEST_RESOURCES / "nav_tree/test_folder/markdown-exec.md"
code_block = mk.MkCode.for_file(path)
info = mk.MkAdmonition(INFO, title="Markdown-Exec rocks!")

print(header)
print(code_block)
print(info)
````

**This can all be very confusing**.

<details>
<summary>Page info</summary>

<details>
<summary>Resources</summary>

```python
Resources(css=[],
          markdown_extensions={},
          plugins=[],
          js=[],
          assets=[],
          packages=[])
```

</details>

<details>
<summary>Metadata</summary>

```yaml
created:
  source_filename: /home/runner/work/mknodes/mknodes/src/mknodes/manual/navs_section.py
  source_function: _
  source_line_no: 24
hide: toc
title: Markdown-Exec

```

</details>

</details>
