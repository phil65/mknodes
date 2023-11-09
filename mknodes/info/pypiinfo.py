from __future__ import annotations

import json

from mknodes.utils import downloadhelpers, log


logger = log.get_logger(__name__)

URL = "https://pypi.org/pypi/{name}/json"


class PyPiInfo:
    def __init__(self, pkg_name: str):
        self.package_name = pkg_name
        url = URL.format(name=self.package_name)
        text = downloadhelpers.download(url).decode()
        self.response = json.loads(text)

    @property
    def summary(self) -> str | None:
        return self.response["info"].get("summary")

    @property
    def description(self) -> str | None:
        return self.response["info"].get("description")


if __name__ == "__main__":
    info = PyPiInfo("git_changelog")
    print(info.description)
