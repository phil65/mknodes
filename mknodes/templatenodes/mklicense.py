from __future__ import annotations

from typing import Any

from mknodes.basenodes import mktext
from mknodes.info import license
from mknodes.utils import log, reprhelpers


logger = log.get_logger(__name__)


class MkLicense(mktext.MkText):
    """Node to show a license.

    If not explicitely set, the license will be pulled from the project.

    """

    ICON = "material/license"
    STATUS = "new"

    def __init__(
        self,
        license_type: str | None = None,
        **kwargs: Any,
    ):
        """Constructor.

        Arguments:
            license_type: License to show (identifier from https://spdx.org/licenses/)
                          If none is set, it will try to get license from Project
            kwargs: Keyword arguments passed to parent
        """
        super().__init__(**kwargs)
        self.license = license_type

    def __repr__(self):
        return reprhelpers.get_repr(self, license=self.license, _filter_empty=True)

    @property
    def text(self):
        if self.license:
            lic = license.License.from_name(self.license)
            lic.resolve_by_distribution(self.ctx.metadata.distribution_name)
            return lic.content
        return self.ctx.metadata.license_text or ""

    @staticmethod
    def create_example_page(page):
        import mknodes

        node = MkLicense()
        page += mknodes.MkReprRawRendered(node, header="### From project")
        node = MkLicense("GPL-3.0")
        page += mknodes.MkReprRawRendered(node, header="### Explicit")


if __name__ == "__main__":
    lic = MkLicense.with_default_context("GPL-3.0")
    print(lic.text)
