from __future__ import annotations

import logging

from typing import Any, Literal

from mknodes.basenodes import mktext
from mknodes.utils import helpers


logger = logging.getLogger(__name__)

URL_END = "/code_of_conduct/code_of_conduct.md"
URL_START = "https://www.contributor-covenant.org/version/"


class MkCodeOfConduct(mktext.MkText):
    """Contributor Covenant code of conduct."""

    ICON = "octicons/code-of-conduct-24"

    def __init__(
        self,
        contact_email: str | None = None,
        version: Literal["2.0", "2.1"] = "2.1",
        header: str = "# Contributor Covenant Code of Conduct",
        **kwargs: Any,
    ):
        """Constructor.

        Arguments:
            contact_email: Email for contacting. If None, it will be pulled from Project.
            version: Contributor covenant version
            header: Section header
            kwargs: Keyword arguments passed to parent
        """
        super().__init__(header=header, **kwargs)
        self.version = version
        self.contact_email = contact_email

    def __repr__(self):
        return helpers.get_repr(
            self,
            contact_email=self.contact_email,
            version=self.version,
            _filter_empty=True,
        )

    @property
    def text(self) -> str:
        url = URL_START + self.version.replace(".", "/") + URL_END
        response = helpers.download(url) or "**Download failed**"
        match self.contact_email:
            case str():
                mail = self.contact_email
            case None if self.associated_project:
                mail = self.associated_project.info.get_author_email()
            case _:
                mail = "<MAIL NOT SET>"
        text = response.replace("[INSERT CONTACT METHOD]", mail)
        return "\n".join(text.split("\n")[3:])

    @staticmethod
    def create_example_page(page):
        import mknodes

        page.status = "new"  # for the small icon in the left menu
        node = MkCodeOfConduct("my@email.com", version="2.1")
        page += mknodes.MkReprRawRendered(node, header="### Explicit email")
        node = MkCodeOfConduct(version="2.0")
        page += mknodes.MkReprRawRendered(node, header="### Email from project")


if __name__ == "__main__":
    coc = MkCodeOfConduct("my@email.com")
    print(coc)
