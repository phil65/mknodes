from __future__ import annotations

import os

import pytest

from mknodes.info import gitrepository


@pytest.mark.skipif(not bool(os.getenv("CI")), reason="Only run Git tests in CI")
def test_getting_version_for_commit():
    repo = gitrepository.GitRepository.clone_from(
        "https://github.com/phil65/mknodes",
        "testclone",
    )
    assert repo.get_version_for_commit("fdd6a0f6") == "v0.49.5"  # one commit before bump
    assert repo.get_version_for_commit("82b61f02") == "v0.49.5"  # bump commit
    assert repo.get_version_for_commit("0a12a015") == "v0.49.6"  # one commit after bump
