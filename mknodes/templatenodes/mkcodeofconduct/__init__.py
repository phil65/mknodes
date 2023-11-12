from __future__ import annotations

from typing import Any, Literal

from mknodes.templatenodes import mktemplate
from mknodes.utils import log


logger = log.get_logger(__name__)


class MkCodeOfConduct(mktemplate.MkTemplate):
    """Node for a code of conduct section."""

    ICON = "octicons/code-of-conduct-24"

    def __init__(
        self,
        contact_email: str | None = None,
        version: Literal["2.1"] | None = None,
        **kwargs: Any,
    ):
        """Constructor.

        Arguments:
            contact_email: Email for contacting. If None, it will be pulled from Project.
            version: Contributor covenant version (currently only "2.1")
            kwargs: Keyword arguments passed to parent
        """
        super().__init__("output/markdown/template", **kwargs)
        self.version = version
        self._contact_email = contact_email

    @property
    def contact_email(self):
        match self._contact_email:
            case str():
                return self._contact_email
            case None:
                return self.ctx.metadata.author_email or "<MAIL NOT SET>"
            case _:
                raise TypeError(self._contact_email)

    @classmethod
    def create_example_page(cls, page):
        import mknodes as mk

        node = MkCodeOfConduct(contact_email="my@email.com")
        page += mk.MkReprRawRendered(node, header="### Explicit email")
        node = MkCodeOfConduct()
        page += mk.MkReprRawRendered(node, header="### Email from project")


if __name__ == "__main__":
    coc = MkCodeOfConduct("my@email.com")
    print(coc)
