# GitContext

<a id="mknodes.info.contexts.GitContext"></a>

```python
class GitContext
```

Local repository information.

#### <a id="mknodes.info.contexts.GitContext.commits"></a>`commits`

```python
commits: list[Any] = dataclasses.field(default_factory=list)
```

List of last commits (Commit objects from `GitPython`).

#### <a id="mknodes.info.contexts.GitContext.current_author"></a>`current_author`

```python
current_author: str = ''
```

Author email for last commit.

#### <a id="mknodes.info.contexts.GitContext.current_committer"></a>`current_committer`

```python
current_committer: str = ''
```

Committer name for last commit.

#### <a id="mknodes.info.contexts.GitContext.current_date_authored"></a>`current_date_authored`

```python
current_date_authored: dt.datetime | None = None
```

Date authored for last commit.

#### <a id="mknodes.info.contexts.GitContext.current_date_committed"></a>`current_date_committed`

```python
current_date_committed: dt.datetime | None = None
```

Date committed for last commit.

#### <a id="mknodes.info.contexts.GitContext.current_sha"></a>`current_sha`

```python
current_sha: str = ''
```

SHA of last commit.

#### <a id="mknodes.info.contexts.GitContext.edit_uri"></a>`edit_uri`

```python
edit_uri: str | None = None
```

Edit uri (depends on code hoster).

#### <a id="mknodes.info.contexts.GitContext.last_version"></a>`last_version`

```python
last_version: str | None = None
```

Name of last commit tag.

#### <a id="mknodes.info.contexts.GitContext.main_branch"></a>`main_branch`

```python
main_branch: str = ''
```

Name of the main branch of the repo (`master` / `main`).

#### <a id="mknodes.info.contexts.GitContext.repo_hoster"></a>`repo_hoster`

```python
repo_hoster: str = ''
```

Name of the code hoster (for example `GitHub`)

#### <a id="mknodes.info.contexts.GitContext.repo_name"></a>`repo_name`

```python
repo_name: str = ''
```

Name of the git folder.

#### <a id="mknodes.info.contexts.GitContext.__init__"></a>`__init__`

```python
def __init__(main_branch: str = '', repo_name: str = '', commits: list[Any] = list(), repo_hoster: str = '', edit_uri: str | None = None, current_sha: str = '', current_committer: str = '', current_date_committed: dt.datetime | None = None, current_author: str = '', current_date_authored: dt.datetime | None = None, last_version: str | None = None) -> None
```

#### <a id="mknodes.info.contexts.GitContext.__repr__"></a>`__repr__`

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
title: GitContext

```

</details>

</details>
