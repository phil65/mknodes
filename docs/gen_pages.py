"""Generate the code reference pages and navigation."""

from __future__ import annotations as _annotations

import pathlib

import mknodes
from mknodes import manual


HEADER = "Don't write docs. Code them."
WARNING = "This is all very alpha and subject to change."
FOOTER = """Thats it. We created a website without touching any .md file
and without having to care about file paths at at all.
Now check out what we have created!
"""

annotations = mknodes.MkAnnotations()
annotations[1] = "We will use annotations to explain things a bit."  # (1)

# this Nav object is basically the root of everything. It corresponds to your root
# SUMMARY.md.
root_nav = mknodes.MkNav()

# Let's begin with the start page. This is your index.md file.
page = root_nav.add_index_page(hide_toc=True, hide_nav=True)

# The next 6 lines are generating the page you are looking at right now.
page.add_header(HEADER, level=3)
admonition = page.add_admonition(WARNING, typ="danger", title="Warning!")
annotations[2] = admonition  # (2)
page += "This is the source code for building this website:"
code = pathlib.Path(__file__).read_text()
page.add_code(code)
page += annotations
page += FOOTER

# now we will create the nav section and its pages one by one.
manual.create_page_1(root_nav)
manual.create_page_2(root_nav)
manual.create_page_3(root_nav)


# This call will write everything we have done to a virtual folder
# (powered by mkgen-pages)
root_nav.write()
