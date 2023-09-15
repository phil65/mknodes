import mknodes as mk


INTRO_TEXT = """MkNodes also contains some higher-order nodes to quickly put together
a Development section.
"""

SECTION_CODE = "Code for this section"
PAGE_CODE = "Code for this page"

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
    page = nav.add_index_page(hide_toc=True, icon="fontawesome/solid/layer-group")
    page += mk.MkCode.for_object(create_development_section, header=SECTION_CODE)
    page += mk.MkAdmonitionBlock(INTRO_TEXT)


@nav.route.page("Module overview", show_source=True, icon="file-tree-outline")
def create_module_overview_page(page: mk.MkPage):
    """Create the "Module overview" MkPage and attach it to given MkNav."""
    page += mk.MkModuleOverview(maximum_depth=2)


@nav.route.page("Plugin flow", show_source=True, icon="dev-to")
def create_plugin_flow_page(page: mk.MkPage):
    """Create the "Plugin flow" MkPage and attach it to given MkNav."""
    page += mk.MkPluginFlow()


@nav.route.page("CLI", show_source=True, icon="api")
def create_cli_page(page: mk.MkPage):
    """Create the "CLI" MkPage and attach it to given MkNav."""
    page += mk.MkClickDoc()


@nav.route.page("Changelog", show_source=True, icon="format-list-group")
def create_changelog_page(page: mk.MkPage):
    """Create the "Changelog" MkPage and attach it to given MkNav."""
    page += mk.MkChangelog()  # based on "git-changelog" package


@nav.route.page("Code of conduct", show_source=True, icon="octicons/code-of-conduct-24")
def create_coc_page(page: mk.MkPage):
    """Create the "Code of conduct" MkPage and attach it to given MkNav."""
    page += mk.MkCodeOfConduct()


@nav.route.page("Contributing", show_source=True, icon="help")
def create_contribute_page(page: mk.MkPage):
    """Create the "Contributing" MkPage and attach it to given MkNav."""
    page += mk.MkCommitConventions()
    page += mk.MkPullRequestGuidelines()


@nav.route.page("License", show_source=True, hide_toc=True, icon="license")
def create_license_page(page: mk.MkPage):
    """Create the "License" MkPage and attach it to given MkNav."""
    page += mk.MkLicense()


@nav.route.page("Dependencies", show_source=True, hide_toc=True, icon="database")
def create_dependencies_page(page: mk.MkPage):
    """Create the "Dependencies" MkPage and attach it to given MkNav."""
    page += mk.MkDependencyTable()


@nav.route.page("Development environment", show_source=True, icon="dev-to")
def create_dev_environment_page(page: mk.MkPage):
    """Create the "Development environment" MkPage and attach it to given MkNav."""
    page += mk.MkDevEnvSetup()


@nav.route.page("Dev Tools", show_source=True, icon="wrench")
def create_dev_tools_page(page: mk.MkPage):
    """Create the "Tools" MkPage and attach it to given MkNav."""
    page += mk.MkDevTools()
