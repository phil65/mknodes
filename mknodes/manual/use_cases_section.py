import mknodes


INTRO_TEXT = """There are a lot of different ways MkNodes can be used to generate
websites. This section will highlight some of them."""


SECTION_CODE = "Code for this section"
PAGE_CODE = "Code for this page"


use_cases_nav = mknodes.MkNav("Use cases")


def create_use_cases_section(root_nav: mknodes.MkNav):
    """Create the "Development" sub-MkNav."""
    root_nav += use_cases_nav
    page = use_cases_nav.add_index_page(hide_toc=True, icon="fontawesome/solid/flask")
    page += mknodes.MkCode.for_object(create_use_cases_section, header=SECTION_CODE)
    page += mknodes.MkAdmonitionBlock(INTRO_TEXT)


@use_cases_nav.route("Creating a sample website", show_source=True)
def create_default_website_section():
    """Create the "Creating a sample website" MkPage."""
    page = mknodes.MkPage("Creating a sample website", hide_toc=True)
    page += mknodes.MkText("The following config...")
    page += mknodes.MkCode.for_file("docs/mkdocs_mkdocs.yml")
    page += mknodes.MkText("Combined with this CLI call...")
    page += mknodes.MkCode("mknodes build", language="terminal")
    page += mknodes.MkText("Will create this website:")
    url = "https://phil65.github.io/mknodes/mkdocs"
    page += mknodes.MkLink(url, as_button=True, icon="material/web")
    return page


@use_cases_nav.route("Creating a website via config", show_source=True)
def create_custom_website_by_config():
    """Create the "Creating a sample website via config" MkPage."""
    page = mknodes.MkPage("Creating a sample website via config", hide_toc=True)
    page += mknodes.MkText("The following config...")
    page += mknodes.MkCode.for_file("docs/mkdocs_mkdocstrings.yml")
    page += mknodes.MkText("Combined with this CLI call...")
    page += mknodes.MkCode("mknodes build", language="terminal")
    page += mknodes.MkText("Will create this website:")
    url = "https://phil65.github.io/mknodes/mkdocstrings"
    page += mknodes.MkLink(url, as_button=True)
    return page
