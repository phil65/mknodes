import mknodes


INTRO_TEXT = """MkNodes also contains some higher-order nodes to quickly put together
a Development section.
"""

SECTION_CODE = "Code for this section"
PAGE_CODE = "Code for this page"

# this is the nav we will populate via decorators.
dev_nav = mknodes.MkNav("Development")


def create_development_section(root_nav: mknodes.MkNav):
    """Create the "Development" sub-MkNav and attach it to given MkNav."""
    # Now we will create the "Development" section.
    # You might notice that this whole section does not contain any specific
    # reference to mknodes. That is because all nodes containing metadata are
    # dynamically populated depending on the project the tree is connected to.
    # This means that this section could be imported by other packages and be
    # used without any further adaptation.
    root_nav += dev_nav
    page = dev_nav.add_index_page(hide_toc=True, icon="fontawesome/solid/layer-group")
    page += mknodes.MkCode.for_object(create_development_section, header=SECTION_CODE)
    page += mknodes.MkAdmonitionBlock(INTRO_TEXT)


@dev_nav.route("Module overview", show_source=True)
def create_module_overview_page():
    """Create the "Module overview" MkPage and attach it to given MkNav."""
    node = mknodes.MkModuleOverview(maximum_depth=2)
    page = mknodes.MkPage("Module overview", icon=node.ICON)
    page += node
    return page


@dev_nav.route("Plugin flow", show_source=True)
def create_plugin_flow_page():
    """Create the "Plugin flow" MkPage and attach it to given MkNav."""
    node = mknodes.MkPluginFlow()
    page = mknodes.MkPage("Plugin flow", icon=node.ICON)
    page += node
    return page


@dev_nav.route("Changelog", show_source=True)
def create_changelog_page():
    """Create the "Changelog" MkPage and attach it to given MkNav."""
    node = mknodes.MkChangelog()  # based on "git-changelog" package
    page = mknodes.MkPage("Changelog", icon=node.ICON)
    page += node
    return page


@dev_nav.route("Code of conduct", show_source=True)
def create_coc_page():
    """Create the "Code of conduct" MkPage and attach it to given MkNav."""
    node = mknodes.MkCodeOfConduct()
    page = mknodes.MkPage("Code of conduct", icon=node.ICON)
    page += node
    return page


@dev_nav.route("Contributing", show_source=True)
def create_contribute_page():
    """Create the "Contributing" MkPage and attach it to given MkNav."""
    page = mknodes.MkPage("Contributing", icon="material/help")
    page += mknodes.MkCommitConventions()
    page += mknodes.MkPullRequestGuidelines()
    return page


@dev_nav.route("License", show_source=True)
def create_license_page():
    """Create the "License" MkPage and attach it to given MkNav."""
    node = mknodes.MkLicense()
    page = mknodes.MkPage("License", icon=node.ICON, hide_toc=True)
    page += node
    return page


@dev_nav.route("Dependencies", show_source=True)
def create_dependencies_page():
    """Create the "Dependencies" MkPage and attach it to given MkNav."""
    node = mknodes.MkDependencyTable()
    page = mknodes.MkPage("Dependencies", icon=node.ICON, hide_toc=True)
    page += node
    return page


@dev_nav.route("Development environment", show_source=True)
def create_dev_environment_page():
    """Create the "Development environment" MkPage and attach it to given MkNav."""
    node = mknodes.MkDevEnvSetup()
    page = mknodes.MkPage("Development environment", icon=node.ICON)
    page += node
    return page
