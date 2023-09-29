import mknodes as mk

from mknodes import paths
from mknodes.manual import routing
from mknodes.project import Project


DOC_TEXT = """Now lets create the documentation.
This code will show how to build a simple documentation section.
"""

nav = mk.MkNav("Navigation & Pages")

pages_nav = nav.add_nav("MkPage")


def create_navs_section(root_nav: mk.MkNav):
    """Add the complete "The Nodes" section to given MkNav."""
    root_nav += nav

    routing.create_routing_section(nav)

    page = pages_nav.add_index_page(hide="toc")
    page += mk.MkJinjaTemplate("mkpage_index.jinja")

    page = nav.add_index_page(hide="toc")
    variables = dict(create_navs_section=create_navs_section, mknode_cls=mk.MkNav)
    page += mk.MkJinjaTemplate("navs_index.jinja", variables=variables)


@nav.route.nav("From file")
def _(nav: mk.MkNav):
    folder = paths.TEST_RESOURCES / "nav_tree/"
    summary_file = folder / "SUMMARY.md"
    nav.parse.file(summary_file, hide="toc")
    page = nav.add_index_page(hide="toc", icon="file")
    text = summary_file.read_text()
    text = text.replace("](", "] (")  ##
    path = paths.TEST_RESOURCES / "nav_tree/"
    variables = dict(path=path, text=text)
    page += mk.MkJinjaTemplate("nav_from_file.jinja", variables=variables)


@nav.route.nav("From folder")
def _(nav: mk.MkNav):
    """Create a MkNav based on a folder tree containing markup files."""
    folder = paths.TEST_RESOURCES / "nav_tree/test_folder/"
    nav.parse.folder(folder, hide="toc")
    page = nav.add_index_page(hide="toc", icon="folder")
    variables = dict(folder=folder)
    page += mk.MkJinjaTemplate("nav_from_folder.jinja", variables=variables)


@pages_nav.route.page("MkClassPage")
def _(page: mk.MkPage):
    variables = dict(example_class=mk.MkCode)
    page += mk.MkJinjaTemplate("mkclasspage.jinja", variables=variables)


@pages_nav.route.page("MkModulePage")
def _(page: mk.MkPage):
    import mkdocs.config

    variables = dict(example_module=mkdocs.config)
    page += mk.MkJinjaTemplate("mkmodulepage.jinja", variables=variables)


@pages_nav.route.page("Adding to MkPages", hide="toc", status="new")
def _(page: mk.MkPage):
    page += mk.MkAdmonition("You can add other MkNodes to a page sequentially.")
    page += "Adding strings also works, they get converted to MkText nodes."
    page += "### ...and text starting with # will become a MkHeader."
    page += "Every MkPage has a MkFootNotes node built-in[^1]."
    page.footnotes[1] = "Super cool, right?"


@pages_nav.route.page(
    "Metadata",
    status="deprecated",
    search_boost=2.0,
    subtitle="Subtitle",
    description="Description",
)
def _(page: mk.MkPage):
    page += mk.MkJinjaTemplate("page_metadata.jinja")


@pages_nav.route.page("Templates", hide="toc", status="new")
def _(page: mk.MkPage):
    page += mk.MkJinjaTemplate("page_templates.jinja")
    page.template.announce.content = mk.MkMetadataBadges(typ="classifiers")
    page.template.footer.content = mk.MkProgressBar(50)
    code = "information = 'You can even put MkNodes here!'"
    page.template.tabs.content = mk.MkCode(f"{code}")
    page.template.hero.content = mk.MkHeader("A header!")
    page.template.styles.add_css(
        {
            ":root": {
                "--md-primary-fg-color": "#FF0000",
                "--md-primary-fg-color--light": "#FF0000",
                "--md-primary-fg-color--dark": "#FF0000",
            },
        },
    )


# @nav.route.nav("MkDefaultWebsite")
def create_mkdefaultwebsite_section(nav: mk.MkNav):
    proj = Project.for_path("https://github.com/mkdocstrings/mkdocstrings.git")
    website_nav = mk.MkDefaultWebsite(section="MkDocStrings", project=proj)
    nav += website_nav


@nav.route.nav("MkDoc")
def _(nav: mk.MkNav):
    nav = nav.add_nav("MkDoc")

    page = nav.add_index_page(hide="toc", icon="api")
    page += mk.MkAdmonition(DOC_TEXT, typ="tip")
    mknodes_docs = nav.add_doc(
        module=mk,
        filter_by___all__=True,
        class_page="docs/classpage_custom.jinja",
    )
    # now we collect the stuff we want to document.
    mknodes_docs.collect_classes(recursive=True)
