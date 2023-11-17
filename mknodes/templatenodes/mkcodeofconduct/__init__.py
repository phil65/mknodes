from __future__ import annotations

from typing import Any

from mknodes.templatenodes import mktemplate


class MkCodeOfConduct(mktemplate.MkTemplate):
    """Node for a code of conduct section."""

    ICON = "octicons/code-of-conduct-24"

    def __init__(
        self,
        contact_email: str | None = None,
        **kwargs: Any,
    ):
        """Constructor.

        Arguments:
            contact_email: Email for contacting. If None, it will be pulled from Project.
            kwargs: Keyword arguments passed to parent
        """
        super().__init__("output/markdown/template", **kwargs)
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


if __name__ == "__main__":
    coc = MkCodeOfConduct("my@email.com")
    print(coc)
