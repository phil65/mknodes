from __future__ import annotations

import dataclasses
import functools
import json
import pathlib

from typing import Any

from mknodes import paths
from mknodes.info import packageregistry
from mknodes.jinja import environment
from mknodes.utils import log


logger = log.get_logger(__name__)


@functools.cache
def get_db() -> dict[str, Any]:
    path = paths.RESOURCES / "licenses" / "db.json"
    with path.open("r") as file:
        return json.load(file)


@dataclasses.dataclass
class License:
    name: str
    identifier: str
    content: str
    path: str | None = None
    sources: list | None = None
    osi_approved: bool | None = None
    header: str | None = None

    @classmethod
    def from_name(cls, name_or_id: str):
        db = get_db()
        name_or_id = name_or_id.lower()
        for lic in db["licenses"]:
            if name_or_id in {lic["name"].lower(), lic["id"].lower()}:
                path = paths.RESOURCES / "licenses" / "templates" / lic["template"]
                return cls(
                    name=lic["name"],
                    identifier=lic["id"],
                    content=path.read_text(encoding="utf-8"),
                    path=path,
                    sources=lic["sources"],
                    osi_approved=lic["osi_approved"],
                    header=lic["header"],
                )
        raise ValueError(name_or_id)

    @classmethod
    def from_path(cls, path: str):
        p = pathlib.Path(path)
        return cls(
            path=str(p),
            content=p.read_text(encoding="utf-8"),
            name=p.name,
            identifier=p.name,
        )

    def resolve_by_distribution(self, distribution: str):
        info = packageregistry.get_info(distribution)
        env = environment.Environment()

        class Ctx:
            copyright_holder = info.author_name
            organization = info.author_name
            program_description = info.metadata["Summary"]
            program_name = info.name
            program_url = info.repository_url or ""
            program_version = info.metadata["Version"]
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
        env = environment.Environment()

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
