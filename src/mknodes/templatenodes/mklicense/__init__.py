from __future__ import annotations

from typing import Any

from mknodes.basenodes import mktext
from mknodes.info import license as lic
from mknodes.utils import log


logger = log.get_logger(__name__)


class MkLicense(mktext.MkText):
    """Node to show a license.

    If not explicitely set, the license will be pulled from the project.

    """

    ICON = "material/license"
    STATUS = "new"

    def __init__(self, license_type: str | None = None, **kwargs: Any) -> None:
        """Constructor.

        Args:
            license_type: License to show (identifier from https://spdx.org/licenses/)
                          If none is set, it will try to get license from Project
            kwargs: Keyword arguments passed to parent
        """
        super().__init__(**kwargs)
        self.license_type = license_type

    async def get_text(self) -> str:
        if self.license_type:
            obj = await lic.License.from_name(self.license_type)
            return obj.content
        return self.ctx.metadata.license_text or ""


if __name__ == "__main__":
    node = MkLicense.with_context("GPL-3.0")
    print(repr(node))
