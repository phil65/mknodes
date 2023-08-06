``` py title='__main__.create_github_index_md' linenums="79" hl_lines="3"
def create_github_index_md() -> mknodes.MkPage:
    page = mknodes.MkPage("Github index")
    page += mknodes.MkCode.for_object(create_github_index_md)
    page += mknodes.MkHeader("MkNodes", level=1)
    page += mknodes.MkHeader("Don't write docs. Code them.", level=4)
    page += mknodes.MkShields(
        ["build", "version", "status", "black"],
        user="phil65",
        project="mknodes",
    )
    page += mknodes.MkLink(
        "https://phil65.github.io/mknodes/",
        "Read the completely coded documentation!",
    )
    page += mknodes.MkInstallGuide("mknodes", header="How to install")
    page += mknodes.MkClassDiagram(
        mknodes.MkNode,
        mode="subclass_tree",
        direction="LR",
        header="All the nodes!",
    )
    return page

```

# MkNodes

#### Don't write docs. Code them.

[![Github Build](https://github.com/phil65/mknodes/workflows/Build/badge.svg)](https://github.com/phil65/mknodes/actions/)
[![PyPI Latest Version](https://img.shields.io/pypi/v/mknodes.svg)](https://pypi.org/project/mknodes/)
[![Package status](https://img.shields.io/pypi/status/mknodes.svg)](https://pypi.org/project/mknodes/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

[Read the completely coded documentation!](https://phil65.github.io/mknodes/)

## How to install

### pip


The latest released version is available at the [Python
package index](https://pypi.org/project/mknodes).

```sh
pip install mknodes
```


## All the nodes!

```mermaid
graph LR
  1523124571872["mknode.MkNode"]
  1523124568032["mkheader.MkHeader"]
  1523125058000["mktext.MkText"]
  1523125089680["mkcritic.MkCritic"]
  1523125057040["mkcontainer.MkContainer"]
  1523125064720["mkblock.MkBlock"]
  1523125069520["mkhtmlblock.MkHtmlBlock"]
  1523125061840["mkadmonitionblock.MkAdmonitionBlock"]
  1523125075280["mkdetailsblock.MkDetailsBlock"]
  1523125080080["mktabs.MkTabBlock"]
  1523125071440["mkadmonition.MkAdmonition"]
  1523125076240["mkblockquote.MkBlockQuote"]
  1523125058960["mkfootnotes.MkFootNote"]
  1523125059920["mkfootnotes.MkFootNotes"]
  1523125068560["mkpage.MkPage"]
  1523125083920["mktemplatepage.MkTemplatePage"]
  1523124862160["mkclasspage.MkClassPage"]
  1523124843920["mkmodulepage.MkModulePage"]
  1523125060880["mkgrid.MkGridCard"]
  1523125077200["mkgrid.MkGrid"]
  1523125065680["mkcode.MkCode"]
  1523125990240["mkprettyprint.MkPrettyPrint"]
  1523126001760["mkdirectorytree.MkDirectoryTree"]
  1523125996000["mklog.MkLog"]
  1523125067600["mklist.MkList"]
  1523125081040["mktabs.MkTab"]
  1523125082000["mktabcontainer.MkTabContainer"]
  1523125086800["mktabcontainer.MkTabbed"]
  1523126012320["mkreprrawrendered.MkReprRawRendered"]
  1523125084880["mktabcontainer.MkTabbedBlocks"]
  1523125090640["mkannotations.MkAnnotation"]
  1523125098320["mkannotations.MkAnnotations"]
  1523125070480["mknav.MkNav"]
  1523124852560["mkdoc.MkDoc"]
  1523125054160["mklink.MkLink"]
  1523125056080["mkkeys.MkKeys"]
  1523125072400["mkdocstrings.MkDocStrings"]
  1523125066640["mkimage.MkImage"]
  1523125073360["mkbinaryimage.MkBinaryImage"]
  1523125074320["mkdiagram.MkDiagram"]
  1523125088720["mkclassdiagram.MkClassDiagram"]
  1523125079120["mkbasetable.MkBaseTable"]
  1523125078160["mktable.MkTable"]
  1523124866000["mkclasstable.MkClassTable"]
  1523126009440["mkmoduletable.MkModuleTable"]
  1523125096400["mksnippet.MkSnippet"]
  1523125099280["mkiframe.MkIFrame"]
  1523125091600["mkprogressbar.MkProgressBar"]
  1523125082960["mkdefinitionlist.MkDefinitionList"]
  1523124869840["mkinclude.MkInclude"]
  1523124863120["mkshields.MkShields"]
  1523124853520["mkinstallguide.MkInstallGuide"]
  1523126010400["mkchangelog.MkChangelog"]
  1523125986400["mkcodeofconduct.MkCodeOfConduct"]
  1523126017120["mkcommitmessageconvention.MkCommitMessageConvention"]
  1523126015200["mkpullrequestguidelines.MkPullRequestGuidelines"]
  1523125999840["mkcallable.MkCallable"]
  1523124571872 --> 1523124568032
  1523124571872 --> 1523125058000
  1523125058000 --> 1523125089680
  1523124571872 --> 1523125057040
  1523125057040 --> 1523125064720
  1523125064720 --> 1523125069520
  1523125064720 --> 1523125061840
  1523125064720 --> 1523125075280
  1523125064720 --> 1523125080080
  1523125057040 --> 1523125071440
  1523125057040 --> 1523125076240
  1523125057040 --> 1523125058960
  1523125057040 --> 1523125059920
  1523125057040 --> 1523125068560
  1523125068560 --> 1523125083920
  1523125083920 --> 1523124862160
  1523125083920 --> 1523124843920
  1523125057040 --> 1523125060880
  1523125057040 --> 1523125077200
  1523125057040 --> 1523125065680
  1523125065680 --> 1523125990240
  1523125065680 --> 1523126001760
  1523125065680 --> 1523125996000
  1523125057040 --> 1523125067600
  1523125057040 --> 1523125081040
  1523125057040 --> 1523125082000
  1523125082000 --> 1523125086800
  1523125086800 --> 1523126012320
  1523125082000 --> 1523125084880
  1523125057040 --> 1523125090640
  1523125057040 --> 1523125098320
  1523124571872 --> 1523125070480
  1523125070480 --> 1523124852560
  1523124571872 --> 1523125054160
  1523124571872 --> 1523125056080
  1523124571872 --> 1523125072400
  1523124571872 --> 1523125066640
  1523125066640 --> 1523125073360
  1523124571872 --> 1523125074320
  1523125074320 --> 1523125088720
  1523124571872 --> 1523125079120
  1523125079120 --> 1523125078160
  1523125078160 --> 1523124866000
  1523125078160 --> 1523126009440
  1523124571872 --> 1523125096400
  1523124571872 --> 1523125099280
  1523124571872 --> 1523125091600
  1523124571872 --> 1523125082960
  1523124571872 --> 1523124869840
  1523124571872 --> 1523124863120
  1523124571872 --> 1523124853520
  1523124571872 --> 1523126010400
  1523124571872 --> 1523125986400
  1523124571872 --> 1523126017120
  1523124571872 --> 1523126015200
  1523124571872 --> 1523125999840
```
