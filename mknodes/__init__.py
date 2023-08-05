from __future__ import annotations

import pathlib

from .basenodes.mkblock import MkBlock
from .basenodes.mkhtmlblock import MkHtmlBlock
from .basenodes.mkadmonitionblock import MkAdmonitionBlock
from .basenodes.mkdetailsblock import MkDetailsBlock
from .basenodes.mkadmonition import MkAdmonition
from .basenodes.mknode import MkNode
from .basenodes.mklink import MkLink
from .basenodes.mktext import MkText
from .basenodes.mkheader import MkHeader
from .basenodes.mkkeys import MkKeys
from .basenodes.mkgrid import MkGrid
from .basenodes.mkcontainer import MkContainer
from .basenodes.mkcode import MkCode
from .basenodes.mkdocstrings import MkDocStrings
from .basenodes.mkimage import MkImage
from .basenodes.mkbinaryimage import MkBinaryImage
from .basenodes.mklist import MkList
from .basenodes.mkdiagram import MkDiagram
from .basenodes.mktable import MkTable
from .basenodes.mktabcontainer import MkTabbedBlocks, MkTabbed
from .basenodes.mksnippet import MkSnippet
from .basenodes.mkcritic import MkCritic
from .basenodes.mkannotations import MkAnnotations
from .basenodes.mkfootnotes import MkFootNotes
from .basenodes.mkiframe import MkIFrame
from .basenodes.mkprogressbar import MkProgressBar
from .basenodes.mkdefinitionlist import MkDefinitionList

from .pages.mkpage import MkPage
from .pages.mkclasspage import MkClassPage
from .pages.mkmodulepage import MkModulePage

from .mknav import MkNav
from .mkdoc import MkDoc

from .templatenodes.mkinclude import MkInclude
from .templatenodes.mkshields import MkShields
from .templatenodes.mkinstallguide import MkInstallGuide
from .templatenodes.mkchangelog import MkChangelog
from .templatenodes.mkcodeofconduct import MkCodeOfConduct
from .templatenodes.mkcommitmessageconvention import MkCommitMessageConvention
from .templatenodes.mkpullrequestguidelines import MkPullRequestGuidelines
from .templatenodes.mkclassdiagram import MkClassDiagram
from .templatenodes.mkclasstable import MkClassTable
from .templatenodes.mkreprrawrendered import MkReprRawRendered
from .templatenodes.mkprettyprint import MkPrettyPrint
from .templatenodes.mkcallable import MkCallable
from .templatenodes.mkdirectorytree import MkDirectoryTree
from .templatenodes.mklog import MkLog

from .templatenodes.mkmoduletable import MkModuleTable

TEST_RESOURCES = pathlib.Path(__file__).parent.parent / "tests/data/"

__all__ = [
    "MkNode",
    "MkLink",
    "MkBlock",
    "MkHtmlBlock",
    "MkAdmonitionBlock",
    "MkDetailsBlock",
    "MkContainer",
    "MkNav",
    "MkDocStrings",
    "MkText",
    "MkKeys",
    "MkGrid",
    "MkCode",
    "MkImage",
    "MkHeader",
    "MkBinaryImage",
    "MkPage",
    "MkAdmonition",
    "MkDiagram",
    "MkClassDiagram",
    "Connector",
    "MkTable",
    "MkClassTable",
    "MkList",
    "MkClassPage",
    "MkModulePage",
    "MkModuleTable",
    "MkAnnotations",
    "MkFootNotes",
    "MkDoc",
    "MkTabbedBlocks",
    "MkTabbed",
    "MkSnippet",
    "MkShields",
    "MkInclude",
    "MkCritic",
    "MkInstallGuide",
    "MkChangelog",
    "MkCodeOfConduct",
    "MkCommitMessageConvention",
    "MkPullRequestGuidelines",
    "MkIFrame",
    "MkProgressBar",
    "MkDefinitionList",
    "MkReprRawRendered",
    "MkPrettyPrint",
    "MkCallable",
    "MkDirectoryTree",
    "MkLog",
]

__version__ = "0.23.0"
