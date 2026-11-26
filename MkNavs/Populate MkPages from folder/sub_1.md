````python
import mknodes as mk
from mknodes import paths

path = paths.TEST_RESOURCES / "nav_tree/test_folder/markdown-exec.md"
node = mk.MkCode.for_file(path)
print(node)
node = mk.MkAdmonition("MkNodes also works great in combination with Markdown-exec!")
print(node)
````

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
  source_line_no: 37
hide:
- toc

```

</details>

</details>
