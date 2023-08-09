from __future__ import annotations

import logging

from typing import Any

from mknodes.basenodes import mktext
from mknodes.utils import helpers


logger = logging.getLogger(__name__)


class MkLicense(mktext.MkText):
    """MkLicense. Shows license file from associated project."""

    ICON = "material/license"

    def __init__(
        self,
        license_type: str | None = None,
        header="License",
        **kwargs: Any,
    ):
        """Constructor.

        Arguments:
            license_type: License to show
            header: Section header
            kwargs: Keyword arguments passed to parent
        """
        super().__init__(header=header, **kwargs)
        self.license = license_type

    def __repr__(self):
        return helpers.get_repr(self, license=self.license, _filter_empty=True)

    @property
    def text(self):
        if self.license is not None:
            # TODO.
            return self.license
        if proj := self.associated_project:
            license_path = proj.info.get_license_file_path()
            if license_path is not None:
                return license_path.read_text()
            return proj.info.get_license()
        return "Unknown license."

    @staticmethod
    def create_example_page(page):
        import mknodes

        node = MkLicense()
        page += mknodes.MkReprRawRendered(node)


if __name__ == "__main__":
    import mknodes

    proj = mknodes.Project(mknodes)
    nav = proj.get_root()
    lic = MkLicense()
    page = nav.add_page("test")
    page += lic
    nav += page
    print(lic)
