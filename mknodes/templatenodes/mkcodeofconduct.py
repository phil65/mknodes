from __future__ import annotations

import functools

from typing import Any, Literal

from mknodes import paths
from mknodes.basenodes import mktext
from mknodes.utils import log, reprhelpers


logger = log.get_logger(__name__)


@functools.cache
def get_markdown():
    file = paths.RESOURCES / "code_of_conduct_2_1.md"
    text = file.read_text()
    # Cut off first lines containing header
    return "\n".join(text.split("\n")[3:])


class MkCodeOfConduct(mktext.MkText):
    """Node for a code of conduct section."""

    ICON = "octicons/code-of-conduct-24"

    def __init__(
        self,
        contact_email: str | None = None,
        version: Literal["2.1"] | None = None,
        header: str = "# Code of Conduct",
        **kwargs: Any,
    ):
        """Constructor.

        Arguments:
            contact_email: Email for contacting. If None, it will be pulled from Project.
            version: Contributor covenant version (currently only "2.1")
            header: Section header
            kwargs: Keyword arguments passed to parent
        """
        super().__init__(header=header, **kwargs)
        self.version = version
        self.contact_email = contact_email

    def __repr__(self):
        return reprhelpers.get_repr(
            self,
            contact_email=self.contact_email,
            version=self.version,
            _filter_empty=True,
        )

    @property
    def text(self) -> str:
        match self.contact_email:
            case str():
                mail = self.contact_email
            case None if self.associated_project:
                mail = self.associated_project.info.author_email
            case _:
                mail = "<MAIL NOT SET>"
        return get_markdown().replace("[INSERT CONTACT METHOD]", mail)

    @staticmethod
    def create_example_page(page):
        import mknodes

        node = MkCodeOfConduct(contact_email="my@email.com")
        page += mknodes.MkReprRawRendered(node, header="### Explicit email")
        node = MkCodeOfConduct()
        page += mknodes.MkReprRawRendered(node, header="### Email from project")


if __name__ == "__main__":
    coc = MkCodeOfConduct("my@email.com")
    print(coc)
