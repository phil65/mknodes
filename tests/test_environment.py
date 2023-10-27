from __future__ import annotations

from mknodes.jinja import environment, loaders


def test_fsspec_protocol_loader():
    env = environment.Environment()
    env.loader = loaders.FsSpecProtocolPathLoader()
    assert env.get_template("file://docs/icons.jinja").render()


def test_fsspec_filesystem_loader():
    env = environment.Environment()
    env.loader = loaders.FsSpecFileSystemLoader("file")
    assert env.get_template("docs/icons.jinja").render()
    env.loader = loaders.FsSpecFileSystemLoader("file://")
    assert env.get_template("docs/icons.jinja").render()


def test_fsspec_filesystem_loader_with_dir_prefix():
    env = environment.Environment()
    env.loader = loaders.FsSpecFileSystemLoader("dir::file://docs")
    assert env.get_template("icons.jinja").render()
