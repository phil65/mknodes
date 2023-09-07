from __future__ import annotations

import dataclasses
import datetime
import functools
import json
import logging

from mknodes import paths


logger = logging.getLogger(__name__)


@functools.cache
def get_db():
    path = paths.RESOURCES / "licenses" / "db.json"
    with path.open("r") as file:
        return json.load(file)


def get_license(name_or_id: str) -> dict:
    db = get_db()
    name_or_id = name_or_id.lower()
    for lic in db["licenses"]:
        if name_or_id in {lic["name"].lower(), lic["id"].lower()}:
            return lic
    raise ValueError(name_or_id)


@dataclasses.dataclass
class License:
    name: str

    def __post_init__(self):
        lic = get_license(self.name)
        self.path = paths.RESOURCES / "licenses" / "templates" / lic["template"]
        self.id = lic["id"]
        self.name = lic["name"]
        self.sources = lic["sources"]
        self.notes = lic["notes"]
        self.osi_approved = lic["osi_approved"]
        self.header = lic["header"]
        self.content = self.path.read_text(encoding="utf-8")

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
    db = License("BSD-3-Clause")
    db.resolve_template(holder="Phil", package_name="test")
    print(db.content)
