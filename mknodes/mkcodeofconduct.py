from __future__ import annotations

import logging
import os

import requests

from mknodes import mknode


logger = logging.getLogger(__name__)

URL_END = "/code_of_conduct/code_of_conduct.md"
URL_START = "https://www.contributor-covenant.org/version/"


class MkCodeOfConduct(mknode.MkNode):
    """Contributor Covenant code of conduct."""

    def __init__(
        self,
        contact_email: str,
        version: str | tuple[int] = "2.1",
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.version = (
            [str(v) for v in version]
            if isinstance(version, tuple)
            else version.split(".")
        )
        self.email = contact_email

    def _to_markdown(self) -> str:
        url = URL_START + "/".join(self.version) + URL_END
        if token := os.getenv("GH_TOKEN"):
            headers = {"Authorization": f"token {token}"}
            response = requests.get(url, headers=headers)
        else:
            response = requests.get(url)
        return response.text.replace("[INSERT CONTACT METHOD]", self.email)

    @staticmethod
    def create_example_page(page):
        import mknodes

        node = MkCodeOfConduct("my@email.com", version="2.1")
        page += mknodes.MkAdmonition(node, collapsible=True, title="Output")
        page += mknodes.MkHtmlBlock(str(node), header="Markdown")


if __name__ == "__main__":
    coc = MkCodeOfConduct("my@email.com")
    print(coc)
