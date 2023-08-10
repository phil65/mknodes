from __future__ import annotations

import datetime
import logging

from typing import Any

import spdx_lookup

from mknodes.basenodes import mktext
from mknodes.utils import helpers


logger = logging.getLogger(__name__)


def get_spdx_license(name: str, copyright_holder: str):
    lic = spdx_lookup.by_id(name)  # there is also by_name, not sure which one to take
    if not lic:
        return None
    text = lic.template.replace("<year>", str(datetime.date.today().year))
    return text.replace("<copyright holders>", copyright_holder)


class MkLicense(mktext.MkText):
    """MkLicense. Shows license file from associated project."""

    ICON = "material/license"

    def __init__(
        self,
        license_type: str | None = None,
        header: str = "License",
        **kwargs: Any,
    ):
        """Constructor.

        Arguments:
            license_type: License to show (identifier from https://spdx.org/licenses/)
                          If none is set, it will try to get license from Project
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
            if self.associated_project:
                holder = self.associated_project.info.metadata["Author-Email"]
            else:
                holder = ""
            text = get_spdx_license(self.license, copyright_holder=holder)
            return text or ""
        if proj := self.associated_project:
            license_path = proj.info.get_license_file_path()
            if license_path is not None:
                return license_path.read_text()
            return proj.info.get_license()
        return "Unknown license."

    @staticmethod
    def create_example_page(page):
        import mknodes

        page.status = "new"
        node = MkLicense()
        page += mknodes.MkReprRawRendered(node, header="### From project")
        node = MkLicense("GPL-3.0")
        page += mknodes.MkReprRawRendered(node, header="### Explicit")


if __name__ == "__main__":
    import mknodes

    proj = mknodes.Project(mknodes)
    nav = proj.get_root()
    lic = MkLicense("GPL-3.0")
    page = nav.add_page("test")
    page += lic
    nav += page
    print(lic)
