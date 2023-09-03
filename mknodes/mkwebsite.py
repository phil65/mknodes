from __future__ import annotations

import logging

from mknodes import mknav


logger = logging.getLogger(__name__)


class MkWebSite(mknav.MkNav):
    """Nav for showing a module documenation."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        import mknodes

        page = self.add_index_page("Overview", hide_toc=True, hide_nav=True)
        page += mknodes.MkMetadataBadges("classifiers")
        page += mknodes.MkText(r"{{metadata.description}}")
        docs = self.add_doc(section_name="API")
        docs.collect_classes(recursive=True)
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

        page = nav.add_page("Dependencies")
        page += mknodes.MkDependencyTable()

        page = nav.add_page("Module overview")
        page += mknodes.MkModuleOverview(maximum_depth=2)

        if self.associated_project.info.get_entry_points("mkdocs.plugins"):
            page = nav.add_page("Plugin flow")
            page += mknodes.MkPluginFlow()

        node = mknodes.MkLicense()
        page = nav.add_page("License", hide_toc=True)
        page += node

    @classmethod
    def for_project(cls, project):
        root = cls(project=project)
        project.set_root(root)


if __name__ == "__main__":
    doc = MkWebSite(module="mkdocs")
    page = doc.add_class_page(MkWebSite)
    print(page)
