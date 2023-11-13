from __future__ import annotations

from mknodes.info import gitrepository


def test_getting_version_for_commit():
    repo = gitrepository.GitRepository(".")
    assert repo.get_version_for_commit("f0a5d2a4") == "v0.49.5"  # one commit before bump
    assert repo.get_version_for_commit("8b0d540a") == "v0.49.6"  # bump commit
    assert repo.get_version_for_commit("9782d9a5") == "v0.49.6"  # one commit after bump
