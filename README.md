# MkNodes

#### Don't write docs. Code them.

[![PyPI License](https://img.shields.io/pypi/l/mknodes.svg)](https://pypi.org/project/mknodes/)
[![Package status](https://img.shields.io/pypi/status/mknodes.svg)](https://pypi.org/project/mknodes/)
[![Daily downloads](https://img.shields.io/pypi/dd/mknodes.svg)](https://pypi.org/project/mknodes/)
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
[![PyUp](https://pyup.io/repos/github/phil65/mknodes/shield.svg)](https://pyup.io/repos/github/phil65/mknodes/)

[Read the completely coded documentation!](https://phil65.github.io/mknodes/)



## Programatically create web pages

``` py title='__main__.create_github_index_md' linenums="86" hl_lines="3"
def create_github_index_md() -> mk.MkPage:
    page = mk.MkPage("Github index")
    page += mk.MkCode.for_object(create_github_index_md)
    page += mk.MkHeader("MkNodes", level=1)
    page += mk.MkHeader("Don't write docs. Code them.", level=4)
    page += mk.MkShields()
    page += mk.MkLink(DOC_URL, "Read the completely coded documentation!")
    page += mk.MkInstallGuide(header="How to install")
    page += mk.MkHeader("All the nodes!")
    page += mk.MkClassDiagram(mk.MkNode, mode="subclasses", direction="LR")
    return page

```


## Create a website tree


``` py
@nav.route.page("Changelog", icon="format-list-group")
def _(page: mk.MkPage):
    page += mk.MkChangelog()
```


## Powerful templating


``` jinja
{{ "Inlined text" | MkAdmonition(inline="left") }}
```




## How to install

### pip

The latest released version is available at the [Python package index](https://pypi.org/project/mknodes).

``` py
pip install mknodes
```
