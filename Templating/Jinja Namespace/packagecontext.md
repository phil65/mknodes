# PackageContext

<a id="mknodes.info.contexts.PackageContext"></a>

```python
class PackageContext
```

Information about a package.

#### <a id="mknodes.info.contexts.PackageContext.author_email"></a>`author_email`

```python
author_email: str = ''
```

A description for the distribution *[Metadata]*

#### <a id="mknodes.info.contexts.PackageContext.author_name"></a>`author_name`

```python
author_name: str = ''
```

The author name of the distribution *[Metadata]*

#### <a id="mknodes.info.contexts.PackageContext.authors"></a>`authors`

```python
authors: dict[str, str] = dataclasses.field(default_factory=dict)
```

All authors of the distribution *[Metadata]*

#### <a id="mknodes.info.contexts.PackageContext.build_system"></a>`build_system`

```python
build_system: buildsystems.BuildSystem = dataclasses.field(default_factory=lambda: buildsystems.hatch)
```

The build system set as build backend *[pyproject]*

#### <a id="mknodes.info.contexts.PackageContext.classifier_map"></a>`classifier_map`

```python
classifier_map: dict[str, list[str]] = dataclasses.field(default_factory=dict)
```

Distribution classifiers, sorted by category *[Metadata]*

#### <a id="mknodes.info.contexts.PackageContext.classifiers"></a>`classifiers`

```python
classifiers: list[str] = dataclasses.field(default_factory=list)
```

Distribution classifiers *[Metadata]*

#### <a id="mknodes.info.contexts.PackageContext.cli"></a>`cli`

```python
cli: str | None = None
```

The cli package name used by the distribution.

#### <a id="mknodes.info.contexts.PackageContext.cli_info"></a>`cli_info`

```python
cli_info: clinspector.CommandInfo | None = None
```

An object containing information about all cli commands.

#### <a id="mknodes.info.contexts.PackageContext.commit_types"></a>`commit_types`

```python
commit_types: list[commitconventions.CommitTypeStr] = dataclasses.field(default_factory=list)
```

Commit types defined in pyproject mknodes section *[pyproject]*

#### <a id="mknodes.info.contexts.PackageContext.configured_build_systems"></a>`configured_build_systems`

```python
configured_build_systems: list[Any] = dataclasses.field(default_factory=list)
```

A list of build systems which are configured in pyproject *[pyproject]*

#### <a id="mknodes.info.contexts.PackageContext.description"></a>`description`

```python
description: str = ''
```

A description for the distribution *[Metadata]*

#### <a id="mknodes.info.contexts.PackageContext.distribution_name"></a>`distribution_name`

```python
distribution_name: str = ''
```

The name of the distribution *[Metadata]*

#### <a id="mknodes.info.contexts.PackageContext.docstring_style"></a>`docstring_style`

```python
docstring_style: str | None = None
```

The style used for DocStrings.

#### <a id="mknodes.info.contexts.PackageContext.entry_points"></a>`entry_points`

```python
entry_points: epregistry.ModuleEntryPointRegistry = dataclasses.field(default_factory=epregistry.ModuleEntryPointRegistry)
```

A dictionary containing the entry points of the distribution.

#### <a id="mknodes.info.contexts.PackageContext.extras"></a>`extras`

```python
extras: dict[str, folderinfo.PackageExtra] = dataclasses.field(default_factory=dict)
```

The extras of the distribution.

#### <a id="mknodes.info.contexts.PackageContext.griffe_module"></a>`griffe_module`

```python
griffe_module: Module | Alias | None = None
```

The primary import package (griffe object).

#### <a id="mknodes.info.contexts.PackageContext.homepage"></a>`homepage`

```python
homepage: str = ''
```

The main website of the distribution.

#### <a id="mknodes.info.contexts.PackageContext.inventory_url"></a>`inventory_url`

```python
inventory_url: str | None = ''
```

A best guess for an inventory URL for the package.

#### <a id="mknodes.info.contexts.PackageContext.keywords"></a>`keywords`

```python
keywords: list[str] = dataclasses.field(default_factory=list)
```

Distribution keywords *[Metadata]*

#### <a id="mknodes.info.contexts.PackageContext.license_name"></a>`license_name`

```python
license_name: str | None = ''
```

Name of the license

#### <a id="mknodes.info.contexts.PackageContext.license_text"></a>`license_text`

```python
license_text: str | None = ''
```

The complete license text

#### <a id="mknodes.info.contexts.PackageContext.mkdocs_config"></a>`mkdocs_config`

```python
mkdocs_config: mkdocsconfigfile.MkDocsConfigFile | None = None
```

A dict-like File containing the MkDocs config.

#### <a id="mknodes.info.contexts.PackageContext.module"></a>`module`

```python
module: types.ModuleType | None = None
```

The primary import package (module object).

#### <a id="mknodes.info.contexts.PackageContext.package_name"></a>`package_name`

```python
package_name: str = ''
```

Name of the primary import package (`[tool.mknodes] package`, else the one
matching the distribution name, else the first one).

#### <a id="mknodes.info.contexts.PackageContext.package_names"></a>`package_names`

```python
package_names: list[str] = dataclasses.field(default_factory=list)
```

Names of all import packages (top-level modules) of the distribution, primary
package first. See `mknodes.info.projectlayout`.

#### <a id="mknodes.info.contexts.PackageContext.package_repos"></a>`package_repos`

```python
package_repos: list[installmethods.InstallMethod] = dataclasses.field(default_factory=list)
```

Package repositories the distribution is distributed on.
Defined in pyproject mknodes section *[pyproject]*

#### <a id="mknodes.info.contexts.PackageContext.pretty_name"></a>`pretty_name`

```python
pretty_name: str = ''
```

A pretty name for the distribution (like **MkNodes**) *[MkDocs site name]*

#### <a id="mknodes.info.contexts.PackageContext.pyproject_file"></a>`pyproject_file`

```python
pyproject_file: pyproject.PyProject = dataclasses.field(default_factory=pyproject.PyProject.find)
```

A dict-like File containing the PyProject data.

#### <a id="mknodes.info.contexts.PackageContext.repository_name"></a>`repository_name`

```python
repository_name: str = ''
```

The repository name of the distribution.

#### <a id="mknodes.info.contexts.PackageContext.repository_path"></a>`repository_path`

```python
repository_path: pathlib.Path = dataclasses.field(default_factory=pathlib.Path)
```

The path to the local git repository.

#### <a id="mknodes.info.contexts.PackageContext.repository_url"></a>`repository_url`

```python
repository_url: str = ''
```

The URL to the remote code repository.

#### <a id="mknodes.info.contexts.PackageContext.repository_username"></a>`repository_username`

```python
repository_username: str = ''
```

The username for the remote code repository.

#### <a id="mknodes.info.contexts.PackageContext.required_package_names"></a>`required_package_names`

```python
required_package_names: list[str] = dataclasses.field(default_factory=list)
```

The names of the dependencies.

#### <a id="mknodes.info.contexts.PackageContext.required_packages"></a>`required_packages`

```python
required_packages: dict[PackageInfo, Dependency] = dataclasses.field(default_factory=dict)
```

PackageInfos for the dependencies.

#### <a id="mknodes.info.contexts.PackageContext.required_python_version"></a>`required_python_version`

```python
required_python_version: str | None = ''
```

The required python version for the distribution *[Metadata]*

#### <a id="mknodes.info.contexts.PackageContext.social_info"></a>`social_info`

```python
social_info: list[dict[str, str]] = dataclasses.field(default_factory=list)
```

A icon-name -> URL dictionary containing .

#### <a id="mknodes.info.contexts.PackageContext.summary"></a>`summary`

```python
summary: str = ''
```

A summary for the distribution *[Metadata]*

#### <a id="mknodes.info.contexts.PackageContext.task_runners"></a>`task_runners`

```python
task_runners: list[Any] = dataclasses.field(default_factory=list)
```

Task runners used by the distribution.

#### <a id="mknodes.info.contexts.PackageContext.tool_section"></a>`tool_section`

```python
tool_section: superdict.SuperDict[Any] = dataclasses.field(default_factory=superdict.SuperDict)
```

The tool section of the pyproject file.

Comes as a SuperDict. (A Mutable mapping with extended capabilities) *[pyproject]*

#### <a id="mknodes.info.contexts.PackageContext.tools"></a>`tools`

```python
tools: list[tools.Tool] = dataclasses.field(default_factory=list)
```

A list of tools found for the distribution.

#### <a id="mknodes.info.contexts.PackageContext.urls"></a>`urls`

```python
urls: Mapping[str, str] = dataclasses.field(default_factory=dict)
```

A set of URLs related to the distribution.

#### <a id="mknodes.info.contexts.PackageContext.version"></a>`version`

```python
version: str = ''
```

The version of the distribution *[Metadata]*

#### <a id="mknodes.info.contexts.PackageContext.__init__"></a>`__init__`

```python
def __init__(package_name: str = '', package_names: list[str] = list(), module: types.ModuleType | None = None, griffe_module: Module | Alias | None = None, docstring_style: str | None = None, distribution_name: str = '', version: str = '', summary: str = '', description: str = '', author_name: str = '', author_email: str = '', authors: dict[str, str] = dict(), classifiers: list[str] = list(), classifier_map: dict[str, list[str]] = dict(), keywords: list[str] = list(), required_python_version: str | None = '', required_package_names: list[str] = list(), required_packages: dict[PackageInfo, Dependency] = dict(), extras: dict[str, folderinfo.PackageExtra] = dict(), urls: Mapping[str, str] = dict(), homepage: str = '', license_name: str | None = '', license_text: str | None = '', pretty_name: str = '', repository_url: str = '', repository_username: str = '', repository_name: str = '', repository_path: pathlib.Path = pathlib.Path(), mkdocs_config: mkdocsconfigfile.MkDocsConfigFile | None = None, pyproject_file: pyproject.PyProject = pyproject.PyProject.find(), tools: list[tools.Tool] = list(), task_runners: list[Any] = list(), social_info: list[dict[str, str]] = list(), inventory_url: str | None = '', entry_points: epregistry.ModuleEntryPointRegistry = epregistry.ModuleEntryPointRegistry(), cli: str | None = None, cli_info: clinspector.CommandInfo | None = None, build_system: buildsystems.BuildSystem = (lambda: buildsystems.hatch)(), configured_build_systems: list[Any] = list(), tool_section: superdict.SuperDict[Any] = superdict.SuperDict(), commit_types: list[commitconventions.CommitTypeStr] = list(), package_repos: list[installmethods.InstallMethod] = list()) -> None
```

#### <a id="mknodes.info.contexts.PackageContext.__repr__"></a>`__repr__`

```python
def __repr__() -> str
```

<details>
<summary>Page info</summary>

<details>
<summary>Resources</summary>

```python
Resources(css=[],
          markdown_extensions={},
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
  source_filename: /home/runner/work/mknodes/mknodes/src/mknodes/manual/templating_section.py
  source_function: _
  source_line_no: 42
title: PackageContext

```

</details>

</details>
