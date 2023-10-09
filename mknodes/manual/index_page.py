import typing

import mknodes as mk

from mknodes.data import datatypes


def create_index_page(nav: mk.MkNav):
    page = nav.add_page("MkNodes", hide="toc,nav")
    page += mk.MkShields(["version", "status", "codecov"])
    fn_code = mk.MkCode.for_object(create_index_page)
    node = mk.MkAdmonition(content=fn_code, title="")
    for i in typing.get_args(datatypes.AdmonitionTypeStr):
        node = mk.MkAdmonition(content=node, typ=i, title="")
    page += node
