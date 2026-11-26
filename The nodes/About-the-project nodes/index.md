# About-the-project nodes

| Node                                                                                                                                                                                                                           | Docstrings                                                                                                                                                                                                                          | Markdown extensions    |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------- |
| [<img src="https://api.iconify.design/mdi/format-list-group.svg?height=16" alt="format-list-group"> MkChangelog](https://phil65.github.io/mknodes/The nodes/About-the-project nodes/mkchangelog/)                              | Node for a git-based changelog (created by git-changelog).<br><br>!!! note<br>    For building a changelog with Github Actions, the actions/checkout@v4<br>    action needs to have fetch-depth set to 0 (or some other value.)<br> |                        |
| [<img src="https://api.iconify.design/octicon/code-of-conduct-24.svg?height=16" alt="code-of-conduct-24"> MkCodeOfConduct](https://phil65.github.io/mknodes/The nodes/About-the-project nodes/mkcodeofconduct/)                | Node for a code of conduct section.                                                                                                                                                                                                 |                        |
| [<img src="https://api.iconify.design/mdi/license.svg?height=16" alt="license"> MkLicense](https://phil65.github.io/mknodes/The nodes/About-the-project nodes/mklicense/)                                                      | Node to show a license.<br><br>If not explicitely set, the license will be pulled from the project.<br><br>                                                                                                                         |                        |
| [<img src="https://api.iconify.design/mdi/database.svg?height=16" alt="database"> MkDependencyTable](https://phil65.github.io/mknodes/The nodes/About-the-project nodes/mkdependencytable/)                                    | Node for a table showing dependencies for a package.                                                                                                                                                                                | `tables`               |
| [<img src="https://api.iconify.design/mdi/help.svg?height=16" alt="help"> MkInstallGuide](https://phil65.github.io/mknodes/The nodes/About-the-project nodes/mkinstallguide/)                                                  | Node to display an install guide.                                                                                                                                                                                                   |                        |
| [<img src="https://api.iconify.design/simple-icons/conventionalcommits.svg?height=16" alt="conventionalcommits"> MkCommitConventions](https://phil65.github.io/mknodes/The nodes/About-the-project nodes/mkcommitconventions/) | Text node containing Commit message conventions.                                                                                                                                                                                    |                        |
| [<img src="https://api.iconify.design/mdi/wrench.svg?height=16" alt="wrench"> MkDevTools](https://phil65.github.io/mknodes/The nodes/About-the-project nodes/mkdevtools/)                                                      | Node showing information about used dev tools.                                                                                                                                                                                      |                        |
| [<img src="https://api.iconify.design/simple-icons/shieldsdotio.svg?height=16" alt="shieldsdotio"> MkShields](https://phil65.github.io/mknodes/The nodes/About-the-project nodes/mkshields/)                                   | Container for Shields.io / GitHub badges.                                                                                                                                                                                           |                        |
| [<img src="https://api.iconify.design/simple-icons/shieldsdotio.svg?height=16" alt="shieldsdotio"> MkMetadataBadges](https://phil65.github.io/mknodes/The nodes/About-the-project nodes/mkmetadatabadges/)                     | Container node for a list of metadata badges.<br><br>Badges are generated locally using "anybadge" package<br>                                                                                                                      |                        |
| [<img src="https://api.iconify.design/mdi/dependency.svg?height=16" alt="dependency"> MkPipDepTree](https://phil65.github.io/mknodes/The nodes/About-the-project nodes/mkpipdeptree/)                                          | Node to display a mermaid diagram for the dependencies.                                                                                                                                                                             | `pymdownx.superfences` |
| [<img src="https://api.iconify.design/mdi/code-json.svg?height=16" alt="code-json"> MkPyDeps](https://phil65.github.io/mknodes/The nodes/About-the-project nodes/mkpydeps/)                                                    | Node for showing a Dependency graph.                                                                                                                                                                                                |                        |

<details>
<summary>Page info</summary>

<details>
<summary>Code for this section</summary>

**mknodes.manual.nodes_section._**

```python
@nav.route.nav("About-the-project nodes")
def _(nav: mk.MkNav) -> None:
    page = nav.add_page(is_index=True, hide="toc")
    page += create_section_for_nodes(nav, ABOUT_THE_PROJECT_NODES)
    page.created_by = create_section_for_nodes

```

</details>

<details>
<summary>Resources</summary>

```python
Resources(css=[],
          markdown_extensions={'tables': {}},
          plugins=[],
          js=[],
          assets=[],
          packages=[])
```

</details>

<details>
<summary>Metadata</summary>

```yaml
created:
  source_filename: /home/runner/work/mknodes/mknodes/src/mknodes/manual/nodes_section.py
  source_function: _
  source_line_no: 172
hide:
- toc
title: About-the-project nodes

```

</details>

</details>
