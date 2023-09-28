from __future__ import annotations

import mknodes

from mknodes.utils import log


logger = log.get_logger(__name__)


class MkDefaultWebsite(mknodes.MkNav):
    """Nav for showing a module documenation."""

    def __init__(
        self,
        static_pages: dict[str, str | dict | list] | None = None,
        **kwargs,
    ):
        super().__init__(**kwargs)

        page = self.add_index_page("Overview", hide="toc")
        page += mknodes.MkText(page.ctx.metadata.description)
        static_pages = static_pages or {}
        self.parse.json(static_pages)
        docs = self.add_doc(section_name="API")
        docs.collect_classes(recursive=True)
        if proj := self.associated_project:
            proj.theme.announcement_bar = mknodes.MkMetadataBadges("websites")
        if self.ctx.metadata.cli:
            page = self.add_page("CLI", hide="nav")
            page += mknodes.MkClickDoc(show_subcommands=True)

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
        page += mknodes.MkPipDepTree(direction="LR")

        page = nav.add_page("Module overview")
        page += mknodes.MkModuleOverview()

        if "mkdocs.plugins" in self.ctx.metadata.entry_points:
            page = nav.add_page("MkDocs Plugins")
            page += mknodes.MkPluginFlow()

        node = mknodes.MkLicense()
        page = nav.add_page("License", hide="toc")
        page += node

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
