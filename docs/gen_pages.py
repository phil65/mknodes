"""Generate the code reference pages and navigation."""

from __future__ import annotations

import pathlib

import mknodes
from mknodes import manual


HEADER = "Don't write docs. Code them."
WARNING = "This is all very alpha and subject to change."


root_nav = mknodes.Nav()

# Let's start with an intro page.
page = root_nav.add_index_page(hide_toc=True, hide_nav=True)
page.add_header(HEADER, level=3)
page.add_admonition(WARNING, typ="danger", title="Warning!")

page += "This is the source code for building this website:"
code = pathlib.Path(__file__).read_text()
page.add_code(code)
page += "Now check out the different pages!"

manual.create_page_1(root_nav)
manual.create_page_2(root_nav)
manual.create_page_3(root_nav)

# This call will write everything to a virtual folder (powered by mkgen-pages)
root_nav.write()
