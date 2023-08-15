````python exec="on"

import mknodes
from mknodes import paths

INFO = """MkNodes also works great in combination with Markdown-exec! You can embed small
snippets into your existing documentation."""

header = mknodes.MkHeader("Markdown for this page")
path = paths.TEST_RESOURCES / "nav_tree/test_folder/markdown-exec.md"
code_block = mknodes.MkCode.for_file(path, language="md")
info = mknodes.MkAdmonition(INFO, title="Markdown-Exec rocks!")

print(header)
print(code_block)
print(info)
````

**This can all be very confusing**.
