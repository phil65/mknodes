import pathlib

import mknodes
from mknodes import manual


HEADER = "Don't write docs. Code them."
INFO = "This is the source code for building this website:"
FOOTER = """Thats it. We created a website without touching any .md file
and without having to care about file paths at at all.
Now check out what we have created!
"""

annotations = mknodes.MkAnnotations()
annotations[1] = "We will use annotations to explain things a bit."  # (1)

# this Nav is basically the root of everything. It corresponds to your root
# SUMMARY.md and is the root of the tree we are building.
root_nav = mknodes.MkNav()

# now we will create the nav section and its pages one by one.
manual.create_page_1(root_nav)
manual.create_page_2(root_nav)
manual.create_page_3(root_nav)
# Each function here adds another Menu item to the root nav. We will get there later.
# This is the resulting root nav: (3)

# Let's begin with the start page. This is your root index.md file.
page = root_nav.add_index_page("Overview", hide_toc=True, hide_nav=True)

# A page can contain MkNodes which represent Markup.
# We can add them to the pages by using Page.add_ methods or by instanciating our
# nodes and adding them to the page.
page.add_header(HEADER, level=3)
admonition = mknodes.MkAdmonition(INFO, typ="info", title="Built with MkNodes")

page += admonition  # (2)
page += mknodes.MkCode(
    pathlib.Path(__file__).read_text()
)  # this is what youre lookin at.
page += annotations
page += FOOTER  # this is how the resulting Markup looks like: (3)


# nothing is written yet, so we can still modify the tree elements and set the
# annotations here.

annotations[2] = admonition
annotations[3] = str(root_nav)
annotations[4] = mknodes.MkHtmlBlock(str(annotations))  # in raw text: (4)

# This call will write everything we have done to a virtual folder
# (powered by mkgen-pages)
root_nav.write()
