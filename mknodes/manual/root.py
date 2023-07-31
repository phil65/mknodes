import mknodes

from mknodes import manual


HEADER = "Don't write docs. Code them."
INFO = "This is the source code for building this website:"
FOOTER = """Thats it. We created a website without touching any .md file
and without having to care about file paths at at all.
Now check out what we have created!
"""


def create_page():
    annotations = mknodes.MkAnnotations()
    annotations[1] = "We will use annotations to explain things a bit."  # (1)

    # this Nav is basically the root of everything. It corresponds to your root
    # SUMMARY.md and is the root of the tree we are building.
    root_nav = mknodes.MkNav()

    # now we will create the nav sections and its pages one by one.
    # For demonstration purposes, this process is split up into some functions.
    manual.create_nodes_section(root_nav)
    manual.create_documentation_section(root_nav)
    manual.create_internals_section(root_nav)
    manual.create_development_section(root_nav)
    # Each function here adds another Menu item to the root nav. We will get there later.
    annotations[2] = str(root_nav)  # This is the resulting root nav: (2)

    # Let's begin with the start page.
    # We will now create the root index.md file (The page you are lookin at right now.)
    page = root_nav.add_index_page(hide_toc=True, hide_nav=True, icon="octicons/home-24")

    # A page can contain MkNodes which represent Markdown text.
    # We can add them to the pages by using Page.add_xyz methods or by instanciating our
    # nodes and adding them to the page.
    page.add_header(HEADER, level=3)
    admonition = mknodes.MkAdmonition(INFO, typ="info", title="Built with MkNodes")

    page += admonition
    annotations[3] = admonition  # (3)

    page += mknodes.MkCode.for_file(__file__)  # what you are looking at right now.
    page += annotations  # here we add the (invisible) annotations block to the page.

    # nothing is written yet, so we can still modify the tree elements and set the
    # annotations here.
    annotations[4] = mknodes.MkHtmlBlock(str(annotations))  # annotations in raw text: (4)

    page.add_admonition(text=FOOTER, typ="success")
    return root_nav
