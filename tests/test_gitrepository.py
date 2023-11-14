from __future__ import annotations

# from mknodes.info import gitrepository

# fails in CI for the tagged commit

# def test_getting_version_for_commit():
#     repo = gitrepository.GitRepository(".")
#     assert repo.get_version_for_commit("fdd6a0f6") == "v0.49.5"  # one commit before bump
#     assert repo.get_version_for_commit("82b61f02") == "v0.49.5"  # bump commit
#     assert repo.get_version_for_commit("0a12a015") == "v0.49.6"  # one commit after bump
