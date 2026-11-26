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
    # assert repo.code_repository == "GitHub"
    # assert repo.edit_uri == "edit/main/"


def test_version_for_commit_off_main_branch(tmp_path, caplog, monkeypatch):
    import git

    # git hooks (e.g. pre-commit) export GIT_DIR / GIT_INDEX_FILE: don't touch that repo
    for var in [k for k in os.environ if k.startswith("GIT_")]:
        monkeypatch.delenv(var)
    repo = git.Repo.init(tmp_path, initial_branch="main")
    with repo.config_writer() as cw:
        cw.set_value("user", "name", "Test")
        cw.set_value("user", "email", "test@example.com")
    repo.index.commit("first")
    repo.create_tag("v1.0.0")
    repo.git.checkout("--detach")
    detached = repo.index.commit("not on main")

    gitrepo = gitrepository.GitRepository(tmp_path)
    with caplog.at_level("WARNING"):
        assert gitrepo.get_version_for_commit(detached.hexsha) is None
        assert gitrepo.get_version_for_commit("HEAD") is None
    assert not caplog.records


def test_repository_without_origin_remote(tmp_path, monkeypatch):
    import git

    for var in [k for k in os.environ if k.startswith("GIT_")]:
        monkeypatch.delenv(var)
    path = tmp_path / "my-project"
    repo = git.Repo.init(path, initial_branch="main")
    gitrepo = gitrepository.GitRepository(path)
    assert gitrepo.remote_url is None
    assert gitrepo.repo_name == "my-project"
    assert gitrepo.repo_url == ""
    repo.create_remote("upstream", "https://github.com/phil65/other.git")
    gitrepo = gitrepository.GitRepository(path)
    assert gitrepo.repo_name == "other"
    assert gitrepo.repo_url == "https://github.com/phil65/other/"


if __name__ == "__main__":
    pytest.main([__file__])
