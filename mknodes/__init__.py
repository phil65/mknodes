from __future__ import annotations

from .jinja.nodeenvironment import NodeEnvironment

from .basenodes.mkblock import MkBlock
from .basenodes.mkhtmlblock import MkHtmlBlock
from .basenodes.mkcompactadmonition import MkCompactAdmonition
from .basenodes.mkdetailsblock import MkDetailsBlock
from .basenodes.mkadmonition import MkAdmonition
from .basenodes.mknode import MkNode
from .basenodes.mkblockquote import MkBlockQuote
from .basenodes.mklink import MkLink
from .basenodes.mktext import MkText
from .basenodes.mkheader import MkHeader
from .basenodes.mkkeys import MkKeys

# from .basenodes.mkgrid import MkGrid
from .basenodes.mkcontainer import MkContainer
from .basenodes.mkcode import MkCode
from .basenodes._mkdocstrings import MkDocStrings
from .basenodes.mkclidoc import MkCliDoc
from .basenodes.mkicon import MkIcon
from .basenodes.mkimage import MkImage
from .basenodes.mkmaterialbadge import MkMaterialBadge
from .basenodes.mkimagecompare import MkImageCompare
from .basenodes.mkimageslideshow import MkImageSlideshow
from .basenodes.mkbinaryimage import MkBinaryImage
from .basenodes.mklist import MkList
from .basenodes.mkdiagram import MkDiagram
from .basenodes.mktable import MkTable
from .basenodes.mkhtmltable import MkHtmlTable
from .basenodes.mktabcontainer import MkTabContainer
from .basenodes.mktabbedblocks import MkTabbedBlocks
from .basenodes.mktabbed import MkTabbed
from .basenodes.mktabs import MkTab, MkTabBlock
from .basenodes.mkcritic import MkCritic
from .basenodes.mkannotations import MkAnnotations
from .basenodes.mkfootnotes import MkFootNotes
from .basenodes.mkiframe import MkIFrame
from .basenodes.mkprogressbar import MkProgressBar
from .basenodes.mkdefinitionlist import MkDefinitionList
from .basenodes.mkcard import MkCard
from .basenodes.mkshowcase import MkShowcase
from .basenodes.mkspeechbubble import MkSpeechBubble
from .basenodes.mktasklist import MkTaskList
from .basenodes.mktimeline import MkTimeline

from .pages.mkpage import MkPage
from .pages.mkclasspage import MkClassPage
from .pages.mkmodulepage import MkModulePage

from .navs.mknav import MkNav
from .navs.mkdoc import MkDoc

from .templatenodes.mkinclude import MkInclude
from .templatenodes.mkshields import MkShields
from .templatenodes.mkinstallguide import MkInstallGuide
from .templatenodes.mkchangelog import MkChangelog
from .templatenodes.mkcodeofconduct import MkCodeOfConduct
from .templatenodes.mkcommitconventions import MkCommitConventions
from .templatenodes.mkpullrequestguidelines import MkPullRequestGuidelines
from .templatenodes.mkdevenvsetup import MkDevEnvSetup
from .templatenodes.mkdevtools import MkDevTools
from .templatenodes.mkclassdiagram import MkClassDiagram
from .templatenodes.mkclasstable import MkClassTable
from .templatenodes.mkreprrawrendered import MkReprRawRendered
from .templatenodes.mktreeview import MkTreeView
from .templatenodes.mklicense import MkLicense
from .templatenodes.mkdependencytable import MkDependencyTable
from .templatenodes.mkcommandoutput import MkCommandOutput
from .templatenodes.mkbadge import MkBadge
from .templatenodes.mkmetadatabadges import MkMetadataBadges
from .templatenodes.mkcommentedcode import MkCommentedCode
from .templatenodes.mkconfigsetting import MkConfigSetting
from .templatenodes.mkmoduletable import MkModuleTable
from .templatenodes.mkpluginflow import MkPluginFlow
from .templatenodes.mktemplate import MkTemplate
from .templatenodes.mkpydeps import MkPyDeps
from .templatenodes.mkpipdeptree import MkPipDepTree

from .pages.metadata import Metadata
from .pages.pagetemplate import PageTemplate
from .navs.router import Router

from .theme.theme import Theme
from .theme.materialtheme import MaterialTheme


def parse(project=None, **kwargs):
    if project:
        kwargs["context"] = project.context
    from mknodes.navs.navparser import parse_new_style_nav

    pages = kwargs.pop("pages")
    root_nav = MkNav(**kwargs)
    project.root = root_nav
    parse_new_style_nav(root_nav, pages)
    return root_nav


__all__ = [
    "MaterialTheme",
    "Metadata",
    "MkAdmonition",
    "MkAnnotations",
    "MkBadge",
    "MkBinaryImage",
    "MkBlock",
    "MkBlockQuote",
    "MkCard",
    "MkChangelog",
    "MkClassDiagram",
    "MkClassPage",
    "MkClassTable",
    "MkCliDoc",
    # "MkGrid",
    "MkCode",
    "MkCodeOfConduct",
    "MkCommandOutput",
    "MkCommentedCode",
    "MkCommitConventions",
    "MkCompactAdmonition",
    "MkConfigSetting",
    "MkContainer",
    "MkCritic",
    "MkDefinitionList",
    "MkDependencyTable",
    "MkDetailsBlock",
    "MkDevEnvSetup",
    "MkDevTools",
    "MkDiagram",
    "MkDoc",
    "MkDocStrings",
    "MkFootNotes",
    "MkHeader",
    "MkHtmlBlock",
    "MkHtmlTable",
    "MkIFrame",
    "MkIcon",
    "MkImage",
    "MkImageCompare",
    "MkImageSlideshow",
    "MkInclude",
    "MkInstallGuide",
    "MkKeys",
    "MkLicense",
    "MkLink",
    "MkList",
    "MkMaterialBadge",
    "MkMetadataBadges",
    "MkModulePage",
    "MkModuleTable",
    "MkNav",
    "MkNode",
    "MkPage",
    "MkPipDepTree",
    "MkPluginFlow",
    "MkProgressBar",
    "MkPullRequestGuidelines",
    "MkPyDeps",
    "MkReprRawRendered",
    "MkShields",
    "MkShowcase",
    "MkSpeechBubble",
    "MkTab",
    "MkTabBlock",
    "MkTabContainer",
    "MkTabbed",
    "MkTabbedBlocks",
    "MkTable",
    "MkTaskList",
    "MkTemplate",
    "MkText",
    "MkTimeline",
    "MkTreeView",
    "NodeEnvironment",
    "PageTemplate",
    "Router",
    "Theme",
]

__version__ = "0.52.18"
