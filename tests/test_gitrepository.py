from __future__ import annotations

import os

import pytest

from mknodes.info import gitrepository


@pytest.mark.skipif(not bool(os.getenv("CI")), reason="Only run Git tests in CI")
def test_gitrepository():
    repo = gitrepository.GitRepository.clone_from(
        "https://github.com/phil65/mknodes",
        "testclone",
    )
    assert repo.get_version_for_commit("fdd6a0f6") == "v0.49.5"  # one commit before bump
    assert repo.get_version_for_commit("82b61f02") == "v0.49.5"  # bump commit
    assert repo.get_version_for_commit("0a12a015") == "v0.49.6"  # one commit after bump
    assert repo.main_branch == "main"
    assert repo.repo_name == "mknodes"
    assert repo.repo_url == "https://github.com/phil65/mknodes/"
    assert "v0.49.5" in repo.version_changes
    assert repo.code_repository == "GitHub"
    assert repo.edit_uri == "edit/main/"
