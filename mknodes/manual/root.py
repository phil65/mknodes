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
    build = Build()
    project.linkprovider.add_inv_file("https://mkdocstrings.github.io/objects.inv")
    build.on_theme(project.theme)
    return build.on_root(project.root) or project.root


class Build:
    def on_theme(self, theme: mk.Theme):
        theme.error_page.content = mk.MkAdmonition("Page does not exist!")
        if isinstance(theme, mk.MaterialTheme):
            theme.content_area_width = 1300
            theme.tooltip_width = 800
            theme.add_status_icon("js", "fa6-brands:js", "Uses JavaScript")
            theme.add_status_icon("css", "vaadin:css", "Uses CSS")

    def on_root(self, nav: mk.MkNav):
        nav.page_template.announcement_bar = mk.MkMetadataBadges("websites")
        nav += get_started_section.nav
        nav += navs_section.nav
        nav += page_section.nav
        nav += nodes_section.nav
        nav += templating_section.nav
        nav += dev_section.nav
        return nav


if __name__ == "__main__":
    import mknodes as mk

    nav = mk.MkNav()
    bld = Build()
    bld.on_root(nav)
    for node in nav.iter_nodes():
        if isinstance(node, mk.MkPage):
            print(node)
