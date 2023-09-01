from __future__ import annotations

import datetime
import functools
import logging

from typing import Any

import spdx_lookup

from mknodes.basenodes import mktext
from mknodes.utils import reprhelpers


logger = logging.getLogger(__name__)


@functools.cache
def get_spdx_license(name: str):
    if lic := spdx_lookup.by_id(name):
        text = lic.template
    if lic := spdx_lookup.by_name(name):
        text = lic.template.replace("<year>", str(datetime.date.today().year))
    if not text:
        return None
    year = str(datetime.date.today().year)
    text = text.replace("<year>", year)
    text = text.replace("[yyyy]", year)
    text = text.replace("[various years]", year)
    return text.replace(" 2001 ", f" {year} ")


class MkLicense(mktext.MkText):
    """Node to show a license.

    If not explicitely set, the license will be pulled from the project.

    """

    ICON = "material/license"
    STATUS = "new"

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
        return reprhelpers.get_repr(self, license=self.license, _filter_empty=True)

    def get_license(self, license_name: str) -> str:
        if self.associated_project:
            holder = self.associated_project.info.author_name
            summary = self.associated_project.info.metadata["Summary"]
            package_name = self.associated_project.info.name
            website = self.associated_project.folderinfo.repository_url or ""
            email = self.associated_project.info.author_email or ""
        else:
            holder = ""
            summary = ""
            package_name = ""
            website = ""
            email = ""
        text = get_spdx_license(license_name)
        if not text:
            return ""
        # some dumb replacing for popular licenses
        text = text.replace("<copyright holders>", holder)
        text = text.replace("[name of copyright owner]", holder)
        text = text.replace("<name of author>", holder)
        text = text.replace("<owner>", holder)
        text = text.replace("David Griffin", holder)
        text = text.replace("<program>", package_name)
        text = text.replace("Universidad de Palermo, Argentina", holder)
        text = text.replace("http://www.palermo.edu/", website)
        text = text.replace("<phk@FreeBSD.ORG>", email)
        return text.replace(
            "<one line to give the program's name and a brief idea of what it does.>",
            f"{package_name}: {summary}",
        )

    @property
    def text(self):
        if self.license is not None:
            return self.get_license(self.license)
        if proj := self.associated_project:
            if license_path := proj.folderinfo.get_license_file_path():
                return license_path.read_text()
            if proj.info.license_name:
                return self.get_license(proj.info.license_name)
        return "Unknown license."

    @staticmethod
    def create_example_page(page):
        import mknodes

        node = MkLicense()
        page += mknodes.MkReprRawRendered(node, header="### From project")
        node = MkLicense("GPL-3.0")
        page += mknodes.MkReprRawRendered(node, header="### Explicit")


if __name__ == "__main__":
    import mknodes

    proj = mknodes.Project.for_mknodes()
    nav = proj.get_root()
    lic = MkLicense("GPL-3.0")
    page = nav.add_page("test")
    page += lic
    nav += page
    print(lic)
