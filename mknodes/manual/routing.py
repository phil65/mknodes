import mknodes


route_nav = mknodes.MkNav("Routed section")


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
