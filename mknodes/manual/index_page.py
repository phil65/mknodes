import typing

import mknodes

from mknodes.data import datatypes


def create_index_page(nav: mknodes.MkNav):
    page = nav.add_page("Fancy index page", hide="toc,nav")
    page += mknodes.MkShields(["version", "status", "codecov"])
    fn_code = mknodes.MkCode.for_object(create_index_page)
    node = mknodes.MkAdmonition(content=fn_code, title="")
    for i in typing.get_args(datatypes.AdmonitionTypeStr):
        node = mknodes.MkAdmonition(content=node, typ=i, title="")
    page += node
