from __future__ import annotations

from mknodes import mknav
from mknodes.pages import mkpage


class MkBlog(mknav.MkNav):
    def __init__(self, **kwargs):
        super().__init__("blog", **kwargs)
        self.posts = mknav.MkNav("posts", parent=self)
        self.index_page = mkpage.MkPage()
