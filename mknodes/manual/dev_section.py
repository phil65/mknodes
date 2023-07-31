from __future__ import annotations

import mknodes


INTRO_TEXT = """MkNodes also contains some higher-order nodes to quickly put together
a Development section.
"""


def create_development_section(root_nav: mknodes.MkNav):
    dev_nav = root_nav.add_nav("Development")

    overview = dev_nav.add_index_page(hide_toc=True)
    overview += mknodes.MkText(INTRO_TEXT)
    overview += mknodes.MkCode.for_object(create_development_section)
    changelog_page = dev_nav.add_page("Changelog")
    changelog_page += mknodes.MkChangelog()  # based on "git-changelog" package
    coc_page = dev_nav.add_page("Code of conduct")
    coc_page += mknodes.MkCodeOfConduct(contact_email="philipptemminghoff@gmail.com")
    contribute_page = dev_nav.add_page("Contributing")
    contribute_page += mknodes.MkCommitMessageConvention()
    contribute_page += mknodes.MkPullRequestGuidelines()


if __name__ == "__main__":
    nav = mknodes.MkNav()
    create_development_section(nav)
    print(nav.children[0])
