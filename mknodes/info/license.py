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
        website: str,
        email: str,
        summary: str,
    ):
        text = self.content
        year = str(datetime.date.today().year)
        text = text.replace("<year>", year)
        text = text.replace("[yyyy]", year)
        text = text.replace("[various years]", year)
        text = text.replace(" 2001 ", f" {year} ")
        # some dumb replacing for popular licenses
        text = text.replace("<copyright holders>", holder)
        text = text.replace("[name of copyright owner]", holder)
        text = text.replace("<name of author>", holder)
        text = text.replace("<owner>", holder)
        text = text.replace("David Griffin", holder)
        text = text.replace("James Hacker", holder)
        text = text.replace("<program>", package_name)
        text = text.replace("Gnomovision", package_name)
        text = text.replace("Universidad de Palermo, Argentina", holder)
        text = text.replace("http://www.palermo.edu/", website)
        text = text.replace("<phk@FreeBSD.ORG>", email)
        text = text.replace(
            "<one line to give the program's name and a brief idea of what it does.>",
            f"{package_name}: {summary}",
        )
        self.content = text


if __name__ == "__main__":
    db = License("Apache License 1.1")
