from __future__ import annotations

from mknodes.utils import downloadhelpers, log


logger = log.get_logger(__name__)

URL = "https://pypi.org/pypi/{name}/json"


class PyPiInfo:
    def __init__(self, pkg_name: str):
        self.package_name = pkg_name
        url = URL.format(name=self.package_name)
        self.response = downloadhelpers.download(url).decode()


if __name__ == "__main__":
    info = PyPiInfo("git_changelog")
    print(info.response)
