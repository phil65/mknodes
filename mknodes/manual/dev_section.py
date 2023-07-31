import mknodes


INTRO_TEXT = """MkNodes also contains some higher-order nodes to quickly put together
a Development section.
"""


def create_development_section(root_nav: mknodes.MkNav):
    dev_nav = root_nav.add_nav("Development")
    overview = dev_nav.add_index_page(hide_toc=True, icon="fontawesome/solid/layer-group")
    overview += mknodes.MkText(INTRO_TEXT)
    overview += mknodes.MkCode.for_object(create_development_section)
    create_changelog_page(dev_nav)
    create_code_of_conduct_page(dev_nav)
    create_contribute_page(dev_nav)


def create_changelog_page(nav):
    page = nav.add_page("Changelog", icon="material/format-list-group")
    page += mknodes.MkCode.for_object(create_changelog_page)
    page += mknodes.MkChangelog()  # based on "git-changelog" package


def create_code_of_conduct_page(nav):
    page = nav.add_page("Code of conduct", icon="octicons/code-of-conduct-24")
    page += mknodes.MkCode.for_object(create_code_of_conduct_page)
    page += mknodes.MkCodeOfConduct(contact_email="philipptemminghoff@gmail.com")


def create_contribute_page(nav):
    page = nav.add_page("Contributing", icon="material/help")
    page += mknodes.MkCode.for_object(create_contribute_page)
    page += mknodes.MkCommitMessageConvention()
    page += mknodes.MkPullRequestGuidelines()
