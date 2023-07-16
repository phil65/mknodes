from __future__ import annotations

import markdownizer


EXPECTED = """<figure markdown>
  ![Image title](something.png)
  <figcaption>Caption</figcaption>
</figure>
"""


def test_image():
    image = markdownizer.Image(path="something.png", caption="Caption")
    assert str(image) == EXPECTED
