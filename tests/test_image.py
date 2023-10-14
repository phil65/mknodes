from __future__ import annotations

import mknodes as mk


EXPECTED = """<figure markdown>
  ![Image title](something.png)
  <figcaption>Caption</figcaption>
</figure>
"""


def test_image():
    image = mk.MkImage(path="something.png", caption="Caption", title="Image title")
    assert str(image) == EXPECTED
