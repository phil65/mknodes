import mknodes as mk

from mknodes.manual import (
    dev_section,
    get_started_section,
    navs_section,
    nodes_section,
    page_section,
    templating_section,
)


def build(project: mk.Project[mk.MaterialTheme]) -> mk.MkNav:
    project.theme.error_page.content = mk.MkAdmonition("Page does not exist!")
    project.theme.content_area_width = 1300
    project.theme.tooltip_width = 800
    project.linkprovider.add_inv_file("https://mkdocstrings.github.io/objects.inv")

    root_nav = project.get_root()
    root_nav.page_template.announcement_bar = mk.MkMetadataBadges("websites")
    root_nav += get_started_section.nav
    root_nav += navs_section.nav
    root_nav += page_section.nav
    root_nav += nodes_section.nav
    root_nav += templating_section.nav
    root_nav += dev_section.nav
    return root_nav
