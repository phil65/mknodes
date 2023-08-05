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
        max_depth=1,
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
  1762649422208["mknode.MkNode"]
  1762649399168["mkheader.MkHeader"]
  1762679335984["mktext.MkText"]
  1762679324464["mkcontainer.MkContainer"]
  1762679331184["mknav.MkNav"]
  1762679337904["mklink.MkLink"]
  1762679330224["mkkeys.MkKeys"]
  1762679338864["mkdocstrings.MkDocStrings"]
  1762679339824["mkimage.MkImage"]
  1762679341744["mkdiagram.MkDiagram"]
  1762679342704["mkbasetable.MkBaseTable"]
  1762679348464["mksnippet.MkSnippet"]
  1762679377264["mkiframe.MkIFrame"]
  1762679371504["mkprogressbar.MkProgressBar"]
  1762679351344["mkdefinitionlist.MkDefinitionList"]
  1762679355184["mkinclude.MkInclude"]
  1762679369584["mkshields.MkShields"]
  1762679384944["mkinstallguide.MkInstallGuide"]
  1762679187184["mkchangelog.MkChangelog"]
  1762679197744["mkcodeofconduct.MkCodeOfConduct"]
  1762679194864["mkcommitmessageconvention.MkCommitMessageConvention"]
  1762679195824["mkpullrequestguidelines.MkPullRequestGuidelines"]
  1762679170864["mkcallable.MkCallable"]
  1762649422208 --> 1762649399168
  1762649422208 --> 1762679335984
  1762649422208 --> 1762679324464
  1762649422208 --> 1762679331184
  1762649422208 --> 1762679337904
  1762649422208 --> 1762679330224
  1762649422208 --> 1762679338864
  1762649422208 --> 1762679339824
  1762649422208 --> 1762679341744
  1762649422208 --> 1762679342704
  1762649422208 --> 1762679348464
  1762649422208 --> 1762679377264
  1762649422208 --> 1762679371504
  1762649422208 --> 1762679351344
  1762649422208 --> 1762679355184
  1762649422208 --> 1762679369584
  1762649422208 --> 1762679384944
  1762649422208 --> 1762679187184
  1762649422208 --> 1762679197744
  1762649422208 --> 1762679194864
  1762649422208 --> 1762679195824
  1762649422208 --> 1762679170864
```
