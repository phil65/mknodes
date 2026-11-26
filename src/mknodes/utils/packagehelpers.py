import functools
from typing import TYPE_CHECKING, Any

from packaging.markers import Marker
from packaging.requirements import Requirement

from mknodes.utils import log


if TYPE_CHECKING:
    from importlib import metadata


logger = log.get_logger(__name__)


@functools.cache
def get_requires(dist: metadata.Distribution) -> list[str]:
    return dist.requires or []


@functools.cache
def get_marker(marker: str) -> Marker:
    return Marker(marker)


def get_extras(markers: list[Any]) -> list[str]:
    extras: list[str] = []
    for marker in markers:
        match marker:
            case list():
                extras.extend(get_extras(marker))
            case tuple():
                if str(marker[0]) == "extra":
                    extras.append(str(marker[2]))
    return extras


class Dependency:
    def __init__(self, name: str) -> None:
        self.req = Requirement(name)
        self.name = self.req.name
        self._marker = name

    @property
    def marker(self) -> Marker | None:
        return get_marker(self._marker.split(";", maxsplit=1)[-1]) if ";" in self._marker else None

    @functools.cached_property
    def extras(self) -> list[str]:
        return get_extras(self.marker._markers) if self.marker else []

    def __repr__(self) -> str:
        return f"{type(self).__name__}(name={self.name!r})"


@functools.cache
def get_dependency(name: str) -> Dependency:
    return Dependency(name)


@functools.cache
def list_installed_packages() -> dict[str, str]:
    from importlib.metadata import distributions

    return {d.metadata["Name"]: d.metadata["Name"].lower() for d in distributions()}


if __name__ == "__main__":
    eps = list_installed_packages()
    print(eps)
