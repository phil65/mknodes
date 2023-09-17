import mknodes as mk

from mknodes.info import mkdocsconfigfile


INTRO_TEXT = """
There are a lot of different ways MkNodes can be used to generate
websites. This section will highlight some of them.


**MkNodes** can be used in many different ways

* Create complete websites
    * **MkNodes** can be used to create a whole website (like it is done with this page)

* Load existing websites and extend it
    * By using `MkNav.parse.folder` / `MkNav.parse.file` as well as `MkPage.from_file`,
      the existing Markdown pages can become part of our tree
      (which we can then extend programatically)

* Create a subsection with **MkNodes** and reference it from your "static" page.
    * You can also set a section name for your root `MkNav` and reference that from your
      `nav:` section in mkdocs.yml

* Create single static pages / blocks for your page
    You can also just use **MkNodes** to create some Nodes, stringify them and include
    the markdown in your static pages

* Using `Markdown-Exec` or similar inline execution plugins
    You can also embed **MkNodes** code directly by using various plug-ins
    (personal recommendation: `Markdown-Exec`)


"""


SECTION_CODE = "Code for this section"
PAGE_CODE = "Code for this page"


nav = mk.MkNav("Use cases")


def create_use_cases_section(root_nav: mk.MkNav):
    """Create the "Development" sub-MkNav."""
    root_nav += nav
    page = nav.add_index_page(hide="toc")
    page += INTRO_TEXT
    code = mk.MkCode.for_object(create_use_cases_section)
    page += mk.MkAdmonition(code, title=SECTION_CODE, collapsible=True)


@nav.route.page("Creating a sample website", show_source=True, hide="toc")
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


@nav.route.page("Creating a website via config", show_source=True, hide="toc")
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
