import typing

import mknodes as mk

from mknodes.data import datatypes
from mknodes.manual.a_quick_tour import a_quick_tour


nav = mk.MkNav("Get started")


@nav.route.page("Welcome to MkNodes", hide="toc", is_homepage=True)
def _(page: mk.MkPage):
    page += mk.MkShields(["version", "status", "codecov"])
    fn_code = mk.MkCode.for_file(__file__)
    node = mk.MkAdmonition(content=fn_code, title="")
    for i in typing.get_args(datatypes.AdmonitionTypeStr):
        node = mk.MkAdmonition(content=node, typ=i, title="")
    page += node


@nav.route.page("Why should I use MkNodes?", hide="toc")
def _(page: mk.MkPage):
    page += mk.MkJinjaTemplate("why_mknodes.jinja")


page = nav.add_page("A quick node tour", hide="toc")
a_quick_tour(page)
page.created_by = a_quick_tour