from __future__ import annotations

import inspect

import mknodes


INTRO_TEXT = """We will now introduce some nodes."""

IMG_DATA = """<svg width="45pt" height="30pt" version="1.1" viewBox="0 0 15.875 10.583" xmlns="http://www.w3.org/2000/svg">
 <g fill="none" stroke="#000" stroke-width=".17639">
  <path d="m6.1295 3.6601 3.2632 3.2632z"/>
  <path d="m9.3927 3.6601-3.2632 3.2632z"/>
 </g>
</svg>
"""


def create_introduce_the_nodes(root_nav: mknodes.MkNav):
    internals_nav = root_nav.add_nav("The nodes")
    overview = internals_nav.add_page("Overview", hide_toc=True)
    overview += INTRO_TEXT
    overview.add_code(inspect.getsource(create_introduce_the_nodes))
    img = mknodes.MkBinaryImage(data=IMG_DATA, path="test.svg", caption="Thumb")
    overview += img


if __name__ == "__main__":
    nav = mknodes.MkNav()
    create_introduce_the_nodes(nav)
    print(nav.children[0])
