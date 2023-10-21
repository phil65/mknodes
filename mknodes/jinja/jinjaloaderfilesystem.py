from __future__ import annotations

import io

import fsspec
import jinja2

from mknodes.utils import log


logger = log.get_logger(__name__)


class JinjaLoaderFileSystem(fsspec.AbstractFileSystem):
    """A FsSpec Filesystem implementation for jinja environment templates."""

    protocol = "jinja"

    def __init__(self, env: jinja2.Environment):
        super().__init__()
        self.env = env

    def ls(self, path: str, detail: bool = True, **kwargs) -> list[str]:
        if not self.env.loader:
            return []
        paths = self.env.loader.list_templates()
        return [p for p in paths if p.startswith(path)]

    def _open(self, path: str, mode="rb", **kwargs) -> io.BytesIO:
        if not self.env.loader:
            msg = "Environment has no loader set"
            raise RuntimeError(msg)
        src, _filename, _uptodate = self.env.loader.get_source(self.env, path)
        return io.BytesIO(src.encode())


if __name__ == "__main__":
    from mknodes.jinja import loaders as loaders_

    fsspec.register_implementation("jinja", JinjaLoaderFileSystem)
    env = jinja2.Environment(loader=loaders_.resource_loader)
    fs = fsspec.filesystem("jinja", env=env)
    # print(fs.ls(""))
    with fs.open("licenses/templates/TORQUE-1.1.txt") as file:
        print(file.read())
