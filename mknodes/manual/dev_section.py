import mknodes


INTRO_TEXT = """MkNodes also contains some higher-order nodes to quickly put together
a Development section.
"""

SECTION_CODE = "Code for this section"
PAGE_CODE = "Code for this page"


def create_development_section(root_nav: mknodes.MkNav):
    """Create the "Development" sub-MkNav and attach it to given MkNav."""
    # Now we will create the "Development" section.
    # You might notice that this whole section does not contain any specific
    # reference to mknodes. That is because all nodes containing metadata are
    # dynamically populated depending on the project the tree is connected to.
    # This means that this section could be imported by other packages and be
    # used without any further adaptation.
    dev_nav = root_nav.add_nav("Development")
    page = dev_nav.add_index_page(hide_toc=True, icon="fontawesome/solid/layer-group")
    page += mknodes.MkCode.for_object(create_development_section, header=SECTION_CODE)
    page += mknodes.MkAdmonitionBlock(INTRO_TEXT)
    create_changelog_page(dev_nav)
    create_coc_page(dev_nav)
    create_contribute_page(dev_nav)
    create_license_page(dev_nav)
    create_dependencies_page(dev_nav)
    create_dev_environment_page(dev_nav)


def create_changelog_page(nav: mknodes.MkNav):
    """Create the "Changelog" MkPage and attach it to given MkNav."""
    node = mknodes.MkChangelog()  # based on "git-changelog" package
    page = nav.add_page("Changelog", icon=node.ICON)
    page += mknodes.MkCode.for_object(create_changelog_page, header=PAGE_CODE)
    page += node


def create_coc_page(nav: mknodes.MkNav):
    """Create the "Code of conduct" MkPage and attach it to given MkNav."""
    node = mknodes.MkCodeOfConduct()
    page = nav.add_page("Code of conduct", icon=node.ICON)
    page += mknodes.MkCode.for_object(create_coc_page, header=PAGE_CODE)
    page += node


def create_contribute_page(nav: mknodes.MkNav):
    """Create the "Contributing" MkPage and attach it to given MkNav."""
    page = nav.add_page("Contributing", icon="material/help")
    page += mknodes.MkCode.for_object(create_contribute_page, header=PAGE_CODE)
    page += mknodes.MkCommitConventions()
    page += mknodes.MkPullRequestGuidelines()


def create_license_page(nav: mknodes.MkNav):
    """Create the "License" MkPage and attach it to given MkNav."""
    node = mknodes.MkLicense()
    page = nav.add_page("License", icon=node.ICON, hide_toc=True)
    page += mknodes.MkCode.for_object(create_license_page, header=PAGE_CODE)
    page += node


def create_dependencies_page(nav: mknodes.MkNav):
    """Create the "Dependencies" MkPage and attach it to given MkNav."""
    node = mknodes.MkDependencyTable()
    page = nav.add_page("Dependencies", icon=node.ICON, hide_toc=True)
    page += mknodes.MkCode.for_object(create_dependencies_page, header=PAGE_CODE)
    page += node


def create_dev_environment_page(nav: mknodes.MkNav):
    """Create the "Development environment" MkPage and attach it to given MkNav."""
    node = mknodes.MkDevEnvSetup()
    page = nav.add_page("Development environment", icon=node.ICON)
    page += mknodes.MkCode.for_object(create_dev_environment_page, header=PAGE_CODE)
    page += node
