import mknodes

from mknodes.basenodes import mkadmonition


def create_index_page(nav: mknodes.MkNav):
    page = nav.add_page("Fancy index page", hide_toc=True, hide_nav=True)
    page += mknodes.MkShields(
        shields=["version", "status", "codecov"],
        user="phil65",
        project="mknodes",
    )
    code = mknodes.MkCode.for_object(create_index_page)
    node = mknodes.MkAdmonition(content=code, title="")
    for i in mkadmonition.AdmonitionTypeStr.__args__:
        node = mknodes.MkAdmonition(content=node, typ=i, title="")
    page += node
    node = mknodes.MkAdmonition(content=mknodes.MkCode(str(page)), title="You did it!")
    for i in mkadmonition.AdmonitionTypeStr.__args__:
        node = mknodes.MkAdmonition(
            content=node,
            typ=i,
            collapsible=True,
            title="Open me to see the markup!",
        )
    page += node
