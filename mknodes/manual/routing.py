"""MkNodes routing example.

MkNodes also supports setting up Navs via decorators. The
decorated functions need to return either an MkPage or another MkNav.
"""

import mknodes


NAV_TEXT = """You can also use decorators to attach MkNavs. These navs then can continue
to build the tree without using decorators (by adding sub-navs).
"""

# this is the nav we will populate via decorators.
route_nav = mknodes.MkNav("Using decorators")


def create_routing_section(nav: mknodes.MkNav):
    """Attaches the router nav to given nav."""
    nav += route_nav
    page = route_nav.add_index_page(icon="material/call-split", hide_toc=True)
    page += mknodes.MkCode.for_file(__file__, header="Code for this section")
    page += mknodes.MkDocStrings(mknodes.MkNav.route, header="MkNav.route Docstrings")


@route_nav.route("Routed page", show_source=True)
def routed_page() -> mknodes.MkPage:
    """Builds a MkPage and attaches it to the router MkNav."""
    page = mknodes.MkPage("Routing to pages")
    page += mknodes.MkAdmonition("Routed page content!")
    return page


@route_nav.route("Routed", "Deeply", "Nested", "Page", show_source=True)
def routed_nested_page() -> mknodes.MkPage:
    """Builds a nested MkPage and attaches it to the router MkNav."""
    page = mknodes.MkPage("Routing to nested pages")
    page += mknodes.MkAdmonition("Nested Routed page content!")
    return page


@route_nav.route("Routed", "Deeply", "Nested", "Nav", show_source=True)
def routed_section() -> mknodes.MkNav:
    """Builds a nested MkNav and attaches it to the router MkNav."""
    section = mknodes.MkNav("Routing to navs")
    index_page = section.add_index_page()
    index_page += mknodes.MkAdmonition(NAV_TEXT)
    page = section.add_page("Routed section page")
    page += mknodes.MkAdmonition("Routed section page content")
    return section
