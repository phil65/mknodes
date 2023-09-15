import mknodes as mk


INTRO_TEXT = """There are a lot of different ways MkNodes can be used to generate
websites. This section will highlight some of them."""


SECTION_CODE = "Code for this section"
PAGE_CODE = "Code for this page"


nav = mk.MkNav("Use cases")


def create_use_cases_section(root_nav: mk.MkNav):
    """Create the "Development" sub-MkNav."""
    root_nav += nav
    page = nav.add_index_page(hide_toc=True, icon="fontawesome/solid/flask")
    page += mk.MkCode.for_object(create_use_cases_section, header=SECTION_CODE)
    page += mk.MkAdmonitionBlock(INTRO_TEXT)


@nav.route.page("Creating a sample website", show_source=True, hide_toc=True)
def create_default_website_section(page: mk.MkPage):
    """Create the "Creating a sample website" MkPage."""
    page += mk.MkText("The following config...")
    page += mk.MkCode.for_file("configs/mkdocs_mkdocs.yml")
    page += mk.MkText("Combined with this CLI call...")
    page += mk.MkCode("mknodes build", language="terminal")
    page += mk.MkText("Will create this website:")
    url = "https://phil65.github.io/mknodes/mkdocs"
    page += mk.MkLink(url, as_button=True, icon="material/web")


@nav.route.page("Creating a website via config", show_source=True, hide_toc=True)
def create_custom_website_by_config(page: mk.MkPage):
    """Create the "Creating a sample website via config" MkPage."""
    page += mk.MkText("The following config...")
    page += mk.MkCode.for_file("configs/mkdocs_mkdocstrings.yml")
    page += mk.MkText("Combined with this CLI call...")
    page += mk.MkCode("mknodes build", language="terminal")
    page += mk.MkText("Will create this website:")
    url = "https://phil65.github.io/mknodes/mkdocstrings"
    page += mk.MkLink(url, as_button=True)
