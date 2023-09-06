from __future__ import annotations

from mknodes.treelib import noderesolver


def test_resolver(project):
    resolver = noderesolver.MkNodeResolver()
    result = resolver.glob("*/*/MkAdm*", project._root)
    assert result


def resolving_files(project):
    project.all_files()
