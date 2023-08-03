import mknodes

from mknodes import manual


HEADER = "Don't write docs. Code them."
INFO = "This is the source code for building this website:"
FOOTER = """We are done! This code created the whole website.
We will now go through each section and explain how we created it.
This is done by prepending the code used to create each section / page to the beginning
of every page of this website. We will now start by creating a fancy start page before
explaining all the MkNodes!
"""


def create_page():
    annotations = mknodes.MkAnnotations()
    annotations[1] = "We will use annotations to explain things a bit."  # (1)

    # this Nav is basically the root of everything. It corresponds to your root
    # SUMMARY.md and is the root of the complete tree we are building during this tour.
    root_nav = mknodes.MkNav()

    # now we will create the nav sections and its pages one by one.
    # For demonstration purposes, this process is split up into several functions.
    # Each function here adds another Menu item to the root nav (aka the tabs at the top).
    # We will get there later.
    manual.create_nodes_section(root_nav)
    manual.create_internals_section(root_nav)
    manual.create_development_section(root_nav)
    annotations[2] = str(root_nav)  # This is the root nav after it was modified: (2)

    # Lets begin with the start page (aka the root index.md).
    # This is the page you are lookin at right now.)
    page = root_nav.add_index_page(hide_toc=True, hide_nav=True, icon="octicons/home-24")

    # A MkPage can contain MkNodes which represent Markdown text.
    # We can add them to the page by using Page.add_xyz methods or by instanciating our
    # nodes and adding them to the page.
    page.add_header(HEADER, level=3)
    admonition = mknodes.MkAdmonition(INFO, typ="info", title="Built with MkNodes")
    page += admonition  # This adds (3)

    # Now we add the MkNode you are looking at right now.
    # We will use MkCode.for_file / MkCode.for_object quite a lot in the next sections.
    # DocStrings for for_file: (4)
    page += mknodes.MkCode.for_file(__file__)
    page += annotations  # here we add the (invisible) annotations block to the page.

    # Finally, we add some annotations we used:
    docs = mknodes.MkDocStrings(mknodes.MkCode.for_file, docstring_section_style="list")
    annotations[3] = admonition
    annotations[4] = docs
    annotations[5] = mknodes.MkHtmlBlock(str(annotations))  # annotations in raw text: (5)

    page.add_admonition(text=FOOTER, typ="success")
    return root_nav
