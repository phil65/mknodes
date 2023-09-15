"""MkNodes routing example.

MkNodes also supports setting up Navs via decorators.
"""

import mknodes as mk

from mknodes.navs import navrouter


NAV_TEXT = """You can also use decorators to attach MkNavs. These navs then can continue
to build the tree without using decorators (by adding sub-navs).
"""

# this is the nav we will populate via decorators.
nav = mk.MkNav("Using decorators")


def create_routing_section(root_nav: mk.MkNav):
    """Attaches the router nav to given nav."""
    root_nav += nav
    page = nav.add_index_page(icon="material/call-split", hide_toc=True)
    page += mk.MkCode.for_file(__file__, header="Code for this section")
    page += mk.MkDocStrings(navrouter.NavRouter, header="MkNav.route Docstrings")


@nav.route.page("Routed page", show_source=True)
def routed_page(page: mk.MkPage):
    """Builds a MkPage and attaches it to the router MkNav."""
    page += mk.MkAdmonition("I'm a page added via decorators!")


@nav.route.page("Routed", "Deeply", "Nested", "Nested page", show_source=True)
def routed_nested_page(page: mk.MkPage):
    """Builds a nested MkPage and attaches it to the router MkNav."""
    page += mk.MkAdmonition("I'm a nested page added via decorators!")


@nav.route.nav("Routed", "Deeply", "Nested", "Nav", show_source=True)
def routed_nav(nav: mk.MkNav):
    """Builds a nested MkNav and attaches it to the router MkNav."""
    index_page = nav.add_index_page()
    index_page += mk.MkAdmonition(NAV_TEXT)
    page = nav.add_page("Routed section page")
    page += mk.MkAdmonition("Routed section page content")
