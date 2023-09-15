import mknodes as mk


INTRO_TEXT = """MkNodes offers a CLI interface in order to build projects based on
Callables. The CLI is closely aligned to the MkDocs CLI to simplify the usage.

MkNodes CLI is based on Typer and uses a RichHandler for log output.

There are 3 diffent commands right now:

- `mknodes build`: Closely aligned to `mkdocs build`, but with the option to point
to a (remote) repository as well as a Website template in form of a Python Callable.

- `mknodes serve`: Same as `mknodes build`, but for serving the page.

- `mknodes create-config`: Does a test run with given callable and repository and
creates a Config file based on the metadata and extension requirements provided
by the combination of Callable and repository.
"""

SECTION_CODE = "Code for this section"
PAGE_CODE = "Code for this page"

# this is the nav we will populate via decorators.
nav = mk.MkNav("CLI")


def create_cli_section(root_nav: mk.MkNav):
    """Create the "Development" sub-MkNav and attach it to given MkNav."""
    # Now we will create the "Development" section.
    # You might notice that this whole section does not contain any specific
    # reference to mk. That is because all nodes containing metadata are
    # dynamically populated depending on the project the tree is connected to.
    # This means that this section could be imported by other packages and be
    # used without any further adaptation.
    root_nav += nav
    page = nav.add_index_page(hide_toc=True, icon="octicons/command-palette-16")
    page += mk.MkCode.for_object(create_cli_section, header=SECTION_CODE)
    page += mk.MkBinaryImage.for_file("docs/assets/cli.gif")
    page += INTRO_TEXT


@nav.route.page("build", show_source=True, icon="wrench")
def create_build_page(page: mk.MkPage):
    """Create the "CLI" MkPage and attach it to given MkNav."""
    page += mk.MkClickDoc("mknodes.cli:cli", prog_name="build")


@nav.route.page("serve", show_source=True, icon="web")
def create_changelog_page(page: mk.MkPage):
    """Create the "Changelog" MkPage and attach it to given MkNav."""
    page += mk.MkClickDoc("mknodes.cli:cli", prog_name="serve")


@nav.route.page("create-config", show_source=True, icon="folder-wrench")
def create_coc_page(page: mk.MkPage):
    """Create the "Code of conduct" MkPage and attach it to given MkNav."""
    page += mk.MkClickDoc("mknodes.cli:cli", prog_name="create-config")
