import mknodes as mk


INTRO_TEXT = """MkNodes also contains some higher-order nodes to quickly put together
a Development section.
"""

# this is the nav we will populate via decorators.
nav = mk.MkNav("Development")


def create_development_section(root_nav: mk.MkNav):
    """Create the "Development" sub-MkNav and attach it to given MkNav."""
    # Now we will create the "Development" section.
    # You might notice that this whole section does not contain any specific
    # reference to mk. That is because all nodes containing metadata are
    # dynamically populated depending on the project the tree is connected to.
    # This means that this section could be imported by other packages and be
    # used without any further adaptation.
    root_nav += nav
    page = nav.add_index_page(hide="toc")
    page += INTRO_TEXT
    page.created_by = create_development_section


@nav.route.page("Module overview", icon="file-tree-outline")
def create_module_overview_page(page: mk.MkPage):
    page += mk.MkModuleOverview(maximum_depth=2)


@nav.route.page("Plugin flow", icon="dev-to")
def create_plugin_flow_page(page: mk.MkPage):
    page += mk.MkPluginFlow()


@nav.route.page("Changelog", icon="format-list-group")
def create_changelog_page(page: mk.MkPage):
    page += mk.MkChangelog()


@nav.route.page("Code of conduct", icon="octicons/code-of-conduct-24")
def create_coc_page(page: mk.MkPage):
    page += mk.MkCodeOfConduct()


@nav.route.page("Contributing", icon="help")
def create_contribute_page(page: mk.MkPage):
    page += mk.MkCommitConventions()
    page += mk.MkPullRequestGuidelines()


@nav.route.page("License", hide="toc", icon="license")
def create_license_page(page: mk.MkPage):
    page += mk.MkLicense()


@nav.route.page("Dependencies", hide="toc", icon="database")
def create_dependencies_page(page: mk.MkPage):
    page += mk.MkDependencyTable(layout="badge")
    page += mk.MkPipDepTree(direction="LR")


@nav.route.page("Development environment", icon="dev-to")
def create_dev_environment_page(page: mk.MkPage):
    page += mk.MkDevEnvSetup()


@nav.route.page("Dev Tools", icon="wrench")
def create_dev_tools_page(page: mk.MkPage):
    page += mk.MkDevTools()
