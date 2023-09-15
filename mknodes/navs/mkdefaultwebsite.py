from __future__ import annotations

import mknodes

from mknodes.navs import parsenav
from mknodes.utils import log


logger = log.get_logger(__name__)


class MkDefaultWebsite(mknodes.MkNav):
    """Nav for showing a module documenation."""

    def __init__(
        self,
        static_pages: dict[str, str | dict | list] | None = None,
        show_debug_section: bool = False,
        **kwargs,
    ):
        super().__init__(**kwargs)

        page = self.add_index_page("Overview", hide_toc=True, hide_nav=True)
        page += mknodes.MkText(r"metadata.description", is_jinja_expression=True)
        static_pages = static_pages or {}
        parsenav.from_json(static_pages, self)
        docs = self.add_doc(section_name="API")
        docs.collect_classes(recursive=True)
        if proj := self.associated_project:
            proj.theme.announcement_bar = mknodes.MkMetadataBadges("websites")
            if (
                proj.folderinfo.info.get_entry_points("console_scripts")
                and "click" in proj.folderinfo.info.required_package_names
            ):
                page = self.add_page("CLI", hide_nav=True)
                page += mknodes.MkClickDoc()

        nav = self.add_nav("Development")

        page = nav.add_page("Changelog")
        page += mknodes.MkChangelog()

        page = nav.add_page("Code of conduct")
        page += mknodes.MkCodeOfConduct()

        page = nav.add_page("Contributing")
        page += mknodes.MkCommitConventions()
        page += mknodes.MkPullRequestGuidelines()

        page = nav.add_page("Setting up the environment")
        page += mknodes.MkDevEnvSetup()
        page += mknodes.MkDevTools(header="Tools")

        page = nav.add_page("Dependencies")
        page += mknodes.MkDependencyTable()

        page = nav.add_page("Module overview")
        page += mknodes.MkModuleOverview()

        if (proj := self.associated_project) and proj.folderinfo.info.get_entry_points(
            "mkdocs.plugins",
        ):
            page = nav.add_page("MkDocs Plugins")
            page += mknodes.MkPluginFlow()

        node = mknodes.MkLicense()
        page = nav.add_page("License", hide_toc=True)
        page += node
        if show_debug_section:
            self.add_debug_nav()

    def add_debug_nav(self):
        internals_nav = self.add_nav("Debug info")
        page = internals_nav.add_index_page(hide_toc=True, icon="magnify")
        page = internals_nav.add_page("Tree", hide_toc=True, icon="graph")
        # page += mknodes.MkHeader("Node tree.", level=3)
        # text = self.root.get_tree_repr(detailed=False)
        # page += mknodes.MkCode(text, language="")
        page = internals_nav.add_page("Requirements", hide_toc=True, icon="puzzle-edit")
        page += mknodes.MkJinjaTemplate("requirements.md")
        page = internals_nav.add_page("Build Log", hide_toc=True, icon="puzzle-edit")
        page += mknodes.MkText("log() | MkCode", is_jinja_expression=True)

    @classmethod
    def for_project(cls, project, **kwargs):
        root = cls(project=project, **kwargs)
        project.set_root(root)
        return root


if __name__ == "__main__":
    import mknodes

    doc = MkDefaultWebsite.for_project(
        mknodes.Project.for_mknodes(),
        static_pages={
            "Usage": "https://raw.githubusercontent.com/mkdocs/mkdocs/master/docs/getting-started.md",
        },
    )
    print(doc)
