# GitHubContext

<a id="mknodes.info.contexts.GitHubContext"></a>

```python
class GitHubContext
```

Information about the GitHub repo / user.

#### <a id="mknodes.info.contexts.GitHubContext.avatar_url"></a>`avatar_url`

```python
avatar_url: str | None = None
```

The url of the GitHub avatar.

#### <a id="mknodes.info.contexts.GitHubContext.bio"></a>`bio`

```python
bio: str | None = None
```

The user biography.

#### <a id="mknodes.info.contexts.GitHubContext.blog"></a>`blog`

```python
blog: str | None = None
```

The user blog URL.

#### <a id="mknodes.info.contexts.GitHubContext.company"></a>`company`

```python
company: str | None = None
```

The company associated with the user.

#### <a id="mknodes.info.contexts.GitHubContext.default_branch"></a>`default_branch`

```python
default_branch: str = ''
```

The default branch of the repository.

#### <a id="mknodes.info.contexts.GitHubContext.email"></a>`email`

```python
email: str | None = None
```

The user email address.

#### <a id="mknodes.info.contexts.GitHubContext.followers"></a>`followers`

```python
followers: int | None = None
```

The follower count of the user.

#### <a id="mknodes.info.contexts.GitHubContext.gravatar_id"></a>`gravatar_id`

```python
gravatar_id: str | None = None
```

The gravatar id associated with the user.

#### <a id="mknodes.info.contexts.GitHubContext.hireable"></a>`hireable`

```python
hireable: bool | None = None
```

Whether the user is hireable.

#### <a id="mknodes.info.contexts.GitHubContext.location"></a>`location`

```python
location: str | None = None
```

The user location, as set on GitHub.

#### <a id="mknodes.info.contexts.GitHubContext.name"></a>`name`

```python
name: str | None = None
```

The GitHub username.

#### <a id="mknodes.info.contexts.GitHubContext.repo_name"></a>`repo_name`

```python
repo_name: str = ''
```

The repository name.

#### <a id="mknodes.info.contexts.GitHubContext.twitter_username"></a>`twitter_username`

```python
twitter_username: str | None = None
```

The twitter username.

#### <a id="mknodes.info.contexts.GitHubContext.workflows"></a>`workflows`

```python
workflows: list[githarbor.Workflow] = dataclasses.field(default_factory=list)
```

A list of configured workflows.

#### <a id="mknodes.info.contexts.GitHubContext.__init__"></a>`__init__`

```python
def __init__(default_branch: str = '', repo_name: str = '', workflows: list[githarbor.Workflow] = list(), avatar_url: str | None = None, bio: str | None = None, blog: str | None = None, company: str | None = None, email: str | None = None, followers: int | None = None, gravatar_id: str | None = None, hireable: bool | None = None, location: str | None = None, name: str | None = None, twitter_username: str | None = None) -> None
```

#### <a id="mknodes.info.contexts.GitHubContext.__repr__"></a>`__repr__`

```python
def __repr__() -> str
```

#### <a id="mknodes.info.contexts.GitHubContext.from_url"></a>`from_url`

```python
def from_url(url: str) -> GitHubContext
```

Create GitHubContext from a GitHubRepository instance.

**Parameters:**

| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `url` | `str` | URL to the repository. |  |

**Returns:**

| Type | Description |
| --- | --- |
| `GitHubContext` | Populated context instance. |

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
title: GitHubContext

```

</details>

</details>
