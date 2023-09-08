from __future__ import annotations

import dataclasses
import datetime
import functools
import json
import logging
import pathlib

from typing import Any

from mknodes import paths


logger = logging.getLogger(__name__)


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

    def resolve_template(
        self,
        holder: str,
        package_name: str,
        website: str = "",
        email: str = "",
        summary: str = "",
    ):
        text = self.content
        year = str(datetime.date.today().year)
        text = text.replace(r"{{ now().year }}", year)
        text = text.replace(r"{{ metadata.copyright_holder }}", holder)
        text = text.replace(r"{{ metadata.organization }}", holder)
        text = text.replace(r"{{ metadata.program_url }}", website)
        text = text.replace(r"{{ metadata.program_name }}", package_name)
        text = text.replace(r"{{ metadata.program_version }}", "")
        desc = f"{package_name}: {summary}"
        text = text.replace(r"{{ metadata.program_description }}", desc)
        self.content = text


if __name__ == "__main__":
    db = License.from_name("BSD-3-Clause")
    db.resolve_template(holder="Phil", package_name="test")
    print(db)
