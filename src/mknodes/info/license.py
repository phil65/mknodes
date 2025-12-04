from __future__ import annotations

import dataclasses
from typing import TYPE_CHECKING, Any, Self

import anyenv
from anyio import functools as anyio_functools
import upath

from mknodes.utils import log


if TYPE_CHECKING:
    from upath.types import JoinablePathLike


logger = log.get_logger(__name__)
DB_URL = "https://raw.githubusercontent.com/fsfe/reuse-tool/refs/heads/main/src/reuse/resources/licenses.json"


@anyio_functools.cache
async def get_db() -> list[dict[str, Any]]:
    response = await anyenv.get_json(DB_URL, return_type=dict, cache=True)
    return response["licenses"]


@dataclasses.dataclass
class License:
    name: str
    identifier: str
    content: str
    path: str | None = None
    sources: list[str] | None = None
    osi_approved: bool | None = None

    @classmethod
    async def from_name(cls, name_or_id: str) -> Self:
        """Get license based on license name.

        Args:
            name_or_id: Name or id of the license to get.
        """
        db = await get_db()
        name_or_id = name_or_id.lower()
        for lic in db:
            if name_or_id in {lic["name"].lower(), lic["licenseId"].lower()}:
                url = lic["detailsUrl"]
                response = await anyenv.get_json(url, return_type=dict[str, Any], cache=True)
                return cls(
                    name=lic["name"],
                    identifier=lic["licenseId"],
                    content=response["licenseText"],
                    path=url,
                    sources=lic["seeAlso"],
                    osi_approved=lic["isOsiApproved"],
                )
        raise ValueError(name_or_id)

    @classmethod
    def from_path(cls, path: JoinablePathLike) -> Self:
        """Get a license from a file path.

        Args:
            path: Path to get license from.
        """
        p = upath.Uath(path)
        content = p.read_text(encoding="utf-8")
        return cls(path=str(p), content=content, name=p.name, identifier=p.name)


if __name__ == "__main__":

    async def main() -> None:
        db = await License.from_name("BSD-3-Clause")
        print(db)

    import asyncio

    asyncio.run(main())
