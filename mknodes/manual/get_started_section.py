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


@nav.route.page("Installation", hide="toc", icon="grommet-icons:install")
def _(page: mk.MkPage):
    page += mk.MkInstallGuide()


@nav.route.page("Why should I use MkNodes?", hide="toc", icon="ri:question-line")
def _(page: mk.MkPage):
    page += mk.MkTemplate("why_mknodes.jinja")


@nav.route.page("A quick node tour", hide="toc", icon="ic:outline-tour")
def _(page: mk.MkPage):
    page.metadata.render_macros = True
    a_quick_tour(page)


@nav.route.page("Changelog", icon="format-list-group")
def _(page: mk.MkPage):
    page += mk.MkChangelog()
