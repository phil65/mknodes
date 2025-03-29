from __future__ import annotations

import dataclasses
import functools
import pathlib
from typing import Any, Self

import jinjarope

from mknodes.info import packageregistry
from mknodes.utils import log


logger = log.get_logger(__name__)
DB_URL = "https://raw.githubusercontent.com/fsfe/reuse-tool/refs/heads/main/src/reuse/resources/licenses.json"


@functools.cache
def get_db() -> list[dict[str, Any]]:
    import anyenv

    response = anyenv.get_json_sync(DB_URL, return_type=dict, cache=True)
    return response["licenses"]


@dataclasses.dataclass
class License:
    """Class representing a license.

    Args:
        name: Name of the license
        identifier: License identifier
        content: License text content
        path: Path to the license
        sources: License sources
        osi_approved: Whether license is OSI-approved
        header: Optional header for the license.
    """

    name: str
    identifier: str
    content: str
    path: str | None = None
    sources: list[str] | None = None
    osi_approved: bool | None = None

    @classmethod
    def from_name(cls, name_or_id: str) -> Self:
        """Get license based on license name.

        Args:
            name_or_id: Name or id of the license to get.
        """
        import anyenv

        db = get_db()
        name_or_id = name_or_id.lower()
        for lic in db:
            if name_or_id in {lic["name"].lower(), lic["licenseId"].lower()}:
                url = lic["detailsUrl"]
                response = anyenv.get_json_sync(url, return_type=dict, cache=True)
                content = response["licenseText"]
                return cls(
                    name=lic["name"],
                    identifier=lic["licenseId"],
                    content=content,
                    path=url,
                    sources=lic["seeAlso"],
                    osi_approved=lic["isOsiApproved"],
                )
        raise ValueError(name_or_id)

    @classmethod
    def from_path(cls, path: str) -> Self:
        """Get a license from a file path.

        Args:
            path: Path to get license from.
        """
        p = pathlib.Path(path)
        return cls(
            path=str(p),
            content=p.read_text(encoding="utf-8"),
            name=p.name,
            identifier=p.name,
        )

    def resolve_by_distribution(self, distribution: str):
        """Resolve license based on distribution data.

        Args:
            distribution: Distribution to use data from.
        """
        info = packageregistry.get_info(distribution)
        env = jinjarope.Environment()

        class Ctx:
            copyright_holder = info.author_name
            organization = info.author_name
            program_description = info.summary
            program_name = info.name
            program_url = info.repository_url or ""
            program_version = info.version
            email = info.author_email

        env.globals["metadata"] = Ctx
        self.content = env.render_string(self.content)

    def resolve_template(
        self,
        holder: str,
        package_name: str,
        org: str | None = None,
        website: str = "",
        mail_address: str = "",
        summary: str = "",
        version: str = "",
    ):
        """Resolve license template by manually passing needed metadata.

        Args:
            holder: Copyright holder
            package_name: Name of the package the license is used for
            org: Name of the organization
            website: Website of the copyright holders
            mail_address: Mail address of the copyright holder
            summary: Summary of the program the license is used for
            version: Version of the program the license is used for
        """
        env = jinjarope.Environment()

        class Ctx:
            copyright_holder = holder
            organization = org or holder
            program_description = summary
            program_name = package_name
            program_url = website
            program_version = version
            email = mail_address

        env.globals["metadata"] = Ctx
        self.content = env.render_string(self.content)


if __name__ == "__main__":
    db = License.from_name("BSD-3-Clause")
    db.resolve_by_distribution("mknodes")
    print(db)
