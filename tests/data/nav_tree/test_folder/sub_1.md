````python exec="on"

import mknodes as mk
from mknodes import paths

path = paths.TEST_RESOURCES / "nav_tree/test_folder/markdown-exec.md"
node = mk.MkCode.for_file(path)
print(node)
node = mk.MkAdmonition("MkNodes also works great in combination with Markdown-exec!")
print(node)
````
