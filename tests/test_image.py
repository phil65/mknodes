from __future__ import annotations

import mknodes


EXPECTED = """<figure markdown>
  ![Image title](something.png)
  <figcaption>Caption</figcaption>
</figure>
"""


def test_image():
    image = mknodes.Image(path="something.png", caption="Caption")
    assert str(image) == EXPECTED
