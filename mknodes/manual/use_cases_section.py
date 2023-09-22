import mknodes as mk

from mknodes.info import mkdocsconfigfile


nav = mk.MkNav("Use cases")


def create_use_cases_section(root_nav: mk.MkNav):
    """Create the "Development" sub-MkNav."""
    root_nav += nav
    page = nav.add_index_page(hide="toc")
    page += mk.MkJinjaTemplate("use_cases_index.jinja")
    page.created_by = create_use_cases_section


@nav.route.page("Creating a sample website", hide="toc")
def create_default_website_section(page: mk.MkPage):
    """Create the "Creating a sample website" MkPage."""
    page += mk.MkText("The following config...")
    file = mkdocsconfigfile.MkDocsConfigFile("configs/mkdocs_mkdocs.yml")
    section = file.get_section("plugins", "mknodes", keep_path=True)
    page += mk.MkCode(section.serialize("yaml"), language="yaml")
    page += mk.MkText("Combined with this CLI call...")
    page += mk.MkCode("mknodes build", language="terminal")
    page += mk.MkText("Will create this website:")
    url = "https://phil65.github.io/mknodes/mkdocs"
    page += mk.MkLink(url, as_button=True, icon="material/web")


@nav.route.page("Creating a website via config", hide="toc")
def create_custom_website_by_config(page: mk.MkPage):
    """Create the "Creating a sample website via config" MkPage."""
    page += mk.MkText("The following config...")
    file = mkdocsconfigfile.MkDocsConfigFile("configs/mkdocs_mkdocstrings.yml")
    section = file.get_section("plugins", "mknodes", keep_path=True)
    page += mk.MkCode(section.serialize("yaml"), language="yaml")
    page += mk.MkText("Combined with this CLI call...")
    page += mk.MkCode("mknodes build", language="terminal")
    page += mk.MkText("Will create this website:")
    url = "https://phil65.github.io/mknodes/mkdocstrings"
    page += mk.MkLink(url, as_button=True)
