"""MkNodes routing example.

MkNodes also supports setting up Navs via decorators.
"""

import mknodes as mk


NAV_TEXT = """You can also use decorators to attach MkNavs. These navs then can continue
to build the tree without using decorators (by adding sub-navs).
"""

nav = mk.MkNav("Using decorators")


@nav.route.page("Routed page")
def routed_page(page: mk.MkPage):
    """Builds a MkPage and attaches it to the router MkNav."""
    page += mk.MkAdmonition("I'm a page added via decorators!")


@nav.route.page("Routed", "Deeply", "Nested", "Nested page")
def routed_nested_page(page: mk.MkPage):
    """Builds a nested MkPage and attaches it to the router MkNav."""
    page += mk.MkAdmonition("I'm a nested page added via decorators!")


@nav.route.nav("Routed", "Deeply", "Nested", "Nav")
def routed_nav(nav: mk.MkNav):
    """Builds a nested MkNav and attaches it to the router MkNav."""
    index_page = nav.add_page(is_index=True)
    index_page += mk.MkAdmonition(NAV_TEXT)
    page = nav.add_page("Routed section page")
    page += mk.MkAdmonition("Routed section page content")
