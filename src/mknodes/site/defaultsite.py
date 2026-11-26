import importlib
from typing import Any

import mknodes as mk
from mknodes.utils import log


logger = log.get_logger(__name__)


README_NAMES = ("README.md", ".github/README.md", "readme.md")


def add_index_page(nav: mk.MkNav) -> mk.MkPage:
    """Add an index page showing the repository README (or the package description)."""
    page = nav.add_page(is_index=True, hide="toc")
    repo_path = nav.ctx.metadata.repository_path
    readme = next((p for name in README_NAMES if (p := repo_path / name).is_file()), None)
    if readme is not None:
        # A README is plain Markdown, not a template: code examples with `{{ ... }}`
        # must not be rendered by Jinja.
        page.metadata.render_macros = False
        page += mk.MkInclude(readme)
    else:
        page += mk.MkText(nav.ctx.metadata.description)
    return page


def add_api_docs(nav: mk.MkNav, section_name: str = "API") -> mk.MkNav | mk.MkDoc:
    """Add API docs for the import packages of the project.

    One package: an API section for it. Several packages (like `agentpool`,
    `agentpool_config`, ...): an API section with one sub-section per package.
    Packages which fail to import get skipped (with a warning).
    """
    names = nav.ctx.metadata.package_names
    if len(names) <= 1:
        return nav.add_doc(section_name=section_name, recursive=True)
    api = nav.add_nav(section_name)
    for name in names:
        try:
            module = importlib.import_module(name)
        except Exception as e:  # noqa: BLE001
            logger.warning("Skipping API docs for %s: import failed (%s)", name, e)
            continue
        api.add_doc(module=module, section_name=name, recursive=True)
    return api


def populate_default_website(
    nav: mk.MkNav,
    static_pages: dict[str, str | dict | list] | None = None,
) -> mk.MkNav:
    """Fill given nav with a default website: README, API docs, CLI and dev infos."""
    add_index_page(nav)
    if static_pages:
        nav.parse.json(static_pages)
    add_api_docs(nav)
    nav.page_template.announcement_bar = mk.MkMetadataBadges("websites")
    if nav.ctx.metadata.cli or nav.ctx.metadata.cli_info:
        page = nav.add_page("CLI", hide="nav")
        page += mk.MkCliDoc(show_subcommands=True)

    dev_nav = nav.add_nav("Development")

    page = dev_nav.add_page("Changelog")
    page += mk.MkChangelog()

    page = dev_nav.add_page("Contributing")
    page += mk.MkCommitConventions()

    page = dev_nav.add_page("Setting up the environment")
    page += mk.MkDevEnvSetup()
    page += mk.MkDevTools(header="Tools")

    page = dev_nav.add_page("Dependencies")
    page += mk.MkDependencyTable()
    page += mk.MkPipDepTree(direction="LR")

    page = dev_nav.add_page("License", hide="toc")
    page += mk.MkLicense()
    return nav


class MkDefaultWebsite(mk.MkNav):
    """Nav for showing a default website including API docs and environment infos."""

    def __init__(
        self,
        static_pages: dict[str, str | dict | list] | None = None,
        **kwargs: Any,
    ):
        super().__init__(**kwargs)
        populate_default_website(self, static_pages)


async def parse(root: mk.MkNav, theme: mk.Theme, pages: list[Any] | None = None) -> mk.MkNav:
    """Default build function.

    Builds the nav from the `pages` setting if given, otherwise creates a default
    website (README index page, API docs, CLI docs and development infos).
    """
    if not pages:
        populate_default_website(root)
        return root

    from mknodes.navs.navparser import parse_new_style_nav

    await parse_new_style_nav(root, pages)
    return root
