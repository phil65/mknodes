````python exec="on"

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
