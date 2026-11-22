from __future__ import annotations

import pytest

from mknodes.info import mkdocsconfigfile


DEPTH = 5


@pytest.mark.parametrize(
    "entry",
    ["- mknodes", "- mknodes:", "- mknodes:\n      show_page_info: true"],
    ids=["bare", "empty", "with_options"],
)
def test_update_mknodes_section(tmp_path, entry: str):
    path = tmp_path / "mkdocs.yml"
    path.write_text(f"site_name: test\nplugins:\n  - search\n  {entry}\n")
    cfg = mkdocsconfigfile.MkDocsConfigFile(path)
    cfg.update_mknodes_section(repo_url="https://x.org/repo", build_fn="a:b", clone_depth=DEPTH)
    assert cfg.plugins[0] == "search"
    section = cfg.mknodes_config
    assert section["repo_path"] == "https://x.org/repo"
    assert section["build_fn"] == "a:b"
    assert section["clone_depth"] == DEPTH


if __name__ == "__main__":
    pytest.main([__file__])
