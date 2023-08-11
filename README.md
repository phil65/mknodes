``` py title='__main__.create_github_index_md' linenums="82" hl_lines="3"
def create_github_index_md() -> mknodes.MkPage:
    page = mknodes.MkPage("Github index")
    page += mknodes.MkCode.for_object(create_github_index_md)
    page += mknodes.MkHeader("MkNodes", level=1)
    page += mknodes.MkHeader("Don't write docs. Code them.", level=4)
    page += mknodes.MkShields()
    page += mknodes.MkLink(DOC_URL, "Read the completely coded documentation!")
    page += mknodes.MkInstallGuide(header="How to install")
    page += mknodes.MkHeader("All the nodes!")
    page += mknodes.MkClassDiagram(mknodes.MkNode, mode="subclasses", direction="LR")
    return page

```

# MkNodes

#### Don't write docs. Code them.

[![PyPI License](https://img.shields.io/pypi/l/mknodes.svg)](https://pypi.org/project/mknodes/)
[![Package status](https://img.shields.io/pypi/status/mknodes.svg)](https://pypi.org/project/mknodes/)
[![Weekly downloads](https://img.shields.io/pypi/dw/mknodes.svg)](https://pypi.org/project/mknodes/)
[![Weekly downloads](https://img.shields.io/pypi/dw/mknodes.svg)](https://pypi.org/project/mknodes/)
[![Monthly downloads](https://img.shields.io/pypi/dm/mknodes.svg)](https://pypi.org/project/mknodes/)
[![Distribution format](https://img.shields.io/pypi/format/mknodes.svg)](https://pypi.org/project/mknodes/)
[![Wheel availability](https://img.shields.io/pypi/wheel/mknodes.svg)](https://pypi.org/project/mknodes/)
[![Python version](https://img.shields.io/pypi/pyversions/mknodes.svg)](https://pypi.org/project/mknodes/)
[![Implementation](https://img.shields.io/pypi/implementation/mknodes.svg)](https://pypi.org/project/mknodes/)
[![Releases](https://img.shields.io/github/downloads/phil65/mknodes/total.svg)](https://github.com/phil65/mknodes/releases)
[![Github Contributors](https://img.shields.io/github/contributors/phil65/mknodes)](https://github.com/phil65/mknodes/graphs/contributors)
[![Github Discussions](https://img.shields.io/github/discussions/phil65/mknodes)](https://github.com/phil65/mknodes/discussions)
[![Github Forks](https://img.shields.io/github/forks/phil65/mknodes)](https://github.com/phil65/mknodes/forks)
[![Github Issues](https://img.shields.io/github/issues/phil65/mknodes)](https://github.com/phil65/mknodes/issues)
[![Github Issues](https://img.shields.io/github/issues-pr/phil65/mknodes)](https://github.com/phil65/mknodes/pulls)
[![Github Watchers](https://img.shields.io/github/watchers/phil65/mknodes)](https://github.com/phil65/mknodes/watchers)
[![Github Stars](https://img.shields.io/github/stars/phil65/mknodes)](https://github.com/phil65/mknodes/stars)
[![Github Repository size](https://img.shields.io/github/repo-size/phil65/mknodes)](https://github.com/phil65/mknodes)
[![Github last commit](https://img.shields.io/github/last-commit/phil65/mknodes)](https://github.com/phil65/mknodes/commits)
[![Github release date](https://img.shields.io/github/release-date/phil65/mknodes)](https://github.com/phil65/mknodes/releases)
[![Github language count](https://img.shields.io/github/languages/count/phil65/mknodes)](https://github.com/phil65/mknodes)
[![Github commits this week](https://img.shields.io/github/commit-activity/w/phil65/mknodes)](https://github.com/phil65/mknodes)
[![Github commits this month](https://img.shields.io/github/commit-activity/m/phil65/mknodes)](https://github.com/phil65/mknodes)
[![Github commits this year](https://img.shields.io/github/commit-activity/y/phil65/mknodes)](https://github.com/phil65/mknodes)
[![Package status](https://codecov.io/gh/phil65/mknodes/branch/main/graph/badge.svg)](https://codecov.io/gh/phil65/mknodes/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![PyUp](https://pyup.io/repos/github/phil65/mknodes/shield.svg)](https://pyup.io/repos/github/phil65/mknodes/)

[Read the completely coded documentation!](https://phil65.github.io/mknodes/)

## How to install

### pip

The latest released version is available at the [Python package index](https://pypi.org/project/mknodes).

``` py
pip install mknodes
```

## All the nodes!

``` mermaid
graph LR
  2221091714352["mknode.MkNode"]
  2221091724112["mkheader.MkHeader"]
  2221091722160["mktext.MkText"]
  2221092966336["mkchangelog.MkChangelog"]
  2221092971216["mkcodeofconduct.MkCodeOfConduct"]
  2221093014160["mklicense.MkLicense"]
  2221091715328["mkcontainer.MkContainer"]
  2221091710448["mkblock.MkBlock"]
  2221091712400["mkhtmlblock.MkHtmlBlock"]
  2221091717280["mkadmonitionblock.MkAdmonitionBlock"]
  2221091718256["mkdetailsblock.MkDetailsBlock"]
  2221091469376["mktabs.MkTabBlock"]
  2221091719232["mkadmonition.MkAdmonition"]
  2221091721184["mkblockquote.MkBlockQuote"]
  2221091467424["mkfootnotes.MkFootNote"]
  2221091479136["mkfootnotes.MkFootNotes"]
  2221091482064["mkpage.MkPage"]
  2221091507440["mktemplatepage.MkTemplatePage"]
  2221091514272["mkclasspage.MkClassPage"]
  2221091501584["mkmodulepage.MkModulePage"]
  2221091466448["mkgrid.MkGridCard"]
  2221091472304["mkgrid.MkGrid"]
  2221091488896["mkcode.MkCode"]
  2221091474256["mkdiagram.MkDiagram"]
  2221091478160["mkclassdiagram.MkClassDiagram"]
  2221092976096["mktreeview.MkTreeView"]
  2221092980000["mkprettyprint.MkPrettyPrint"]
  2221092995616["mklog.MkLog"]
  2221093038560["mkcommandoutput.MkCommandOutput"]
  2221091475232["mklist.MkList"]
  2221091489872["mkbasetable.MkBaseTable"]
  2221091471328["mktable.MkTable"]
  2221091497680["mkclasstable.MkClassTable"]
  2221093027824["mkdependencytable.MkDependencyTable"]
  2221093033680["mkmoduletable.MkModuleTable"]
  2221091483040["mktabs.MkTab"]
  2221091470352["mktabcontainer.MkTabContainer"]
  2221091484016["mktabcontainer.MkTabbed"]
  2221092977072["mkreprrawrendered.MkReprRawRendered"]
  2221091460592["mktabcontainer.MkTabbedBlocks"]
  2221091484992["mkcritic.MkCritic"]
  2221091480112["mkannotations.MkAnnotation"]
  2221091476208["mkannotations.MkAnnotations"]
  2221091487920["mkdefinitionlist.MkDefinitionList"]
  2221091503536["mkshields.MkShields"]
  2221091517200["mkinstallguide.MkInstallGuide"]
  2221092969264["mkcommitconventions.MkCommitConventions"]
  2221092970240["mkpullrequestguidelines.MkPullRequestGuidelines"]
  2221092974144["mkdevenvsetup.MkDevEnvSetup"]
  2221091465472["mknav.MkNav"]
  2221091515248["mkdoc.MkDoc"]
  2221091491824["mklink.MkLink"]
  2221091486944["mkkeys.MkKeys"]
  2221091463520["mkdocstrings.MkDocStrings"]
  2221091481088["mkimage.MkImage"]
  2221091468400["mkbinaryimage.MkBinaryImage"]
  2221093042464["mkbadge.MkBadge"]
  2221091473280["mksnippet.MkSnippet"]
  2221091485968["mkiframe.MkIFrame"]
  2221091492800["mkprogressbar.MkProgressBar"]
  2221091502560["mkinclude.MkInclude"]
  2221093000496["mkcallable.MkCallable"]
  2221091714352 --> 2221091724112
  2221091714352 --> 2221091722160
  2221091722160 --> 2221092966336
  2221091722160 --> 2221092971216
  2221091722160 --> 2221093014160
  2221091714352 --> 2221091715328
  2221091715328 --> 2221091710448
  2221091710448 --> 2221091712400
  2221091710448 --> 2221091717280
  2221091710448 --> 2221091718256
  2221091710448 --> 2221091469376
  2221091715328 --> 2221091719232
  2221091715328 --> 2221091721184
  2221091715328 --> 2221091467424
  2221091715328 --> 2221091479136
  2221091715328 --> 2221091482064
  2221091482064 --> 2221091507440
  2221091507440 --> 2221091514272
  2221091507440 --> 2221091501584
  2221091715328 --> 2221091466448
  2221091715328 --> 2221091472304
  2221091715328 --> 2221091488896
  2221091488896 --> 2221091474256
  2221091474256 --> 2221091478160
  2221091488896 --> 2221092976096
  2221091488896 --> 2221092980000
  2221091488896 --> 2221092995616
  2221091488896 --> 2221093038560
  2221091715328 --> 2221091475232
  2221091715328 --> 2221091489872
  2221091489872 --> 2221091471328
  2221091471328 --> 2221091497680
  2221091471328 --> 2221093027824
  2221091471328 --> 2221093033680
  2221091715328 --> 2221091483040
  2221091715328 --> 2221091470352
  2221091470352 --> 2221091484016
  2221091484016 --> 2221092977072
  2221091470352 --> 2221091460592
  2221091715328 --> 2221091484992
  2221091715328 --> 2221091480112
  2221091715328 --> 2221091476208
  2221091715328 --> 2221091487920
  2221091715328 --> 2221091503536
  2221091715328 --> 2221091517200
  2221091715328 --> 2221092969264
  2221091715328 --> 2221092970240
  2221091715328 --> 2221092974144
  2221091714352 --> 2221091465472
  2221091465472 --> 2221091515248
  2221091714352 --> 2221091491824
  2221091714352 --> 2221091486944
  2221091714352 --> 2221091463520
  2221091714352 --> 2221091481088
  2221091481088 --> 2221091468400
  2221091468400 --> 2221093042464
  2221091714352 --> 2221091473280
  2221091714352 --> 2221091485968
  2221091714352 --> 2221091492800
  2221091714352 --> 2221091502560
  2221091714352 --> 2221093000496
```
