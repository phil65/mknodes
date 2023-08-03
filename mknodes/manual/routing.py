import mknodes


TITLE = "Setting up Navs via decorators"
TEXT = """MkNodes also supports setting up Navs via decorators. The
decorated functions need to return either an MkPage or another MkNav."""

route_nav = mknodes.MkNav("Using decorators")


def create_routing_section(nav: mknodes.MkNav):
    nav += route_nav
    page = route_nav.add_index_page(icon="material/call-split")
    page += mknodes.MkAdmonition(TEXT, title=TITLE)
    page += mknodes.MkCode.for_file(__file__)


@route_nav.route("Routed page")
def routed_page():
    page = mknodes.MkPage("Routed page")
    page += "Routed page content!"
    return page


@route_nav.route("Routed", "Deeply", "Nested", "Page")
def routed_nested_page():
    page = mknodes.MkPage("Nested page")
    page += "Nested Routed page content!"
    return page


@route_nav.route("Routed", "Deeply", "Nested", "Nav")
def routed_section():
    section = mknodes.MkNav("Routed section")
    index_page = section.add_index_page()
    index_page += "Routed index page content!"
    page = section.add_page("Routed section page")
    page += "Routed section page content"
    return section
