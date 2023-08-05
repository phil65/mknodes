``` py title='mknodes.manual.root.create_github_index_md' linenums="80" hl_lines="3"
def create_github_index_md():
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
        header="All the nodes!"
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
  2002715447360["mknode.MkNode"]
  2002715480000["mkheader.MkHeader"]
  2002745549296["mktext.MkText"]
  2002745581936["mkcontainer.MkContainer"]
  2002745591536["mknav.MkNav"]
  2002745592496["mklink.MkLink"]
  2002745593456["mkkeys.MkKeys"]
  2002745595376["mkdocstrings.MkDocStrings"]
  2002745596336["mkimage.MkImage"]
  2002745598256["mkdiagram.MkDiagram"]
  2002745599216["mkbasetable.MkBaseTable"]
  2002745608816["mksnippet.MkSnippet"]
  2002745635696["mkiframe.MkIFrame"]
  2002745641456["mkprogressbar.MkProgressBar"]
  2002745610736["mkdefinitionlist.MkDefinitionList"]
  2002745628016["mkinclude.MkInclude"]
  2002745630896["mkshields.MkShields"]
  2002745615536["mkinstallguide.MkInstallGuide"]
  2002745711536["mkchangelog.MkChangelog"]
  2002745686576["mkcodeofconduct.MkCodeOfConduct"]
  2002745687536["mkcommitmessageconvention.MkCommitMessageConvention"]
  2002745691376["mkpullrequestguidelines.MkPullRequestGuidelines"]
  2002745700016["mkcallable.MkCallable"]
  2002715447360 --> 2002715480000
  2002715447360 --> 2002745549296
  2002715447360 --> 2002745581936
  2002715447360 --> 2002745591536
  2002715447360 --> 2002745592496
  2002715447360 --> 2002745593456
  2002715447360 --> 2002745595376
  2002715447360 --> 2002745596336
  2002715447360 --> 2002745598256
  2002715447360 --> 2002745599216
  2002715447360 --> 2002745608816
  2002715447360 --> 2002745635696
  2002715447360 --> 2002745641456
  2002715447360 --> 2002745610736
  2002715447360 --> 2002745628016
  2002715447360 --> 2002745630896
  2002715447360 --> 2002745615536
  2002715447360 --> 2002745711536
  2002715447360 --> 2002745686576
  2002715447360 --> 2002745687536
  2002715447360 --> 2002745691376
  2002715447360 --> 2002745700016
```
``` py title='__main__.create_github_index_md' linenums="80" hl_lines="3"
def create_github_index_md():
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
        header="All the nodes!"
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
  2002715447360["mknode.MkNode"]
  2002715480000["mkheader.MkHeader"]
  2002745549296["mktext.MkText"]
  2002745581936["mkcontainer.MkContainer"]
  2002745591536["mknav.MkNav"]
  2002745592496["mklink.MkLink"]
  2002745593456["mkkeys.MkKeys"]
  2002745595376["mkdocstrings.MkDocStrings"]
  2002745596336["mkimage.MkImage"]
  2002745598256["mkdiagram.MkDiagram"]
  2002745599216["mkbasetable.MkBaseTable"]
  2002745608816["mksnippet.MkSnippet"]
  2002745635696["mkiframe.MkIFrame"]
  2002745641456["mkprogressbar.MkProgressBar"]
  2002745610736["mkdefinitionlist.MkDefinitionList"]
  2002745628016["mkinclude.MkInclude"]
  2002745630896["mkshields.MkShields"]
  2002745615536["mkinstallguide.MkInstallGuide"]
  2002745711536["mkchangelog.MkChangelog"]
  2002745686576["mkcodeofconduct.MkCodeOfConduct"]
  2002745687536["mkcommitmessageconvention.MkCommitMessageConvention"]
  2002745691376["mkpullrequestguidelines.MkPullRequestGuidelines"]
  2002745700016["mkcallable.MkCallable"]
  2002715447360 --> 2002715480000
  2002715447360 --> 2002745549296
  2002715447360 --> 2002745581936
  2002715447360 --> 2002745591536
  2002715447360 --> 2002745592496
  2002715447360 --> 2002745593456
  2002715447360 --> 2002745595376
  2002715447360 --> 2002745596336
  2002715447360 --> 2002745598256
  2002715447360 --> 2002745599216
  2002715447360 --> 2002745608816
  2002715447360 --> 2002745635696
  2002715447360 --> 2002745641456
  2002715447360 --> 2002745610736
  2002715447360 --> 2002745628016
  2002715447360 --> 2002745630896
  2002715447360 --> 2002745615536
  2002715447360 --> 2002745711536
  2002715447360 --> 2002745686576
  2002715447360 --> 2002745687536
  2002715447360 --> 2002745691376
  2002715447360 --> 2002745700016
```
