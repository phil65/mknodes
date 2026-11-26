# Contributing

Commit messages must follow the following convention:

```md
<type>[(scope)]: Subject

[Body]
```

**Subject and body must be valid Markdown.**
Subject must have proper casing (uppercase for first letter
if it makes sense), but no dot at the end, and no punctuation
in general.

Scope and body are optional. Type can be:

* `build`: About packaging, building wheels, etc.
* `chore`: About packaging or repo/files management.
* `docs`: About documentation.
* `feat`: New feature.
* `fix`: Bug fix.
* `refactor`: Changes that are not features or bug fixes.
* `test`: About tests.

If you write a body, please add trailers at the end
(for example issues and PR references, or co-authors),
without relying on GitHub's flavored Markdown:

```md
Body.

Issue #10: https://github.com/namespace/project/issues/10
Related to PR namespace/other-project#2: https://github.com/namespace/other-project/pull/2"
```

These "trailers" must appear at the end of the body,
without any blank lines between them. The trailer title
can contain any character except colons `:`.
We expect a full URI for each trailer, not just GitHub autolinks
(for example, full GitHub URLs for commits and issues,
not the hash or the #issue-number).

We do not enforce a line length on commit messages summary and body,
but please avoid very long summaries, and very long lines in the body,
unless they are part of code blocks that must not be wrapped.

<details>
<summary>Page info</summary>

<details>
<summary>Code for this page</summary>

**mknodes.manual.dev_section._**

```python
@nav.route.page("Contributing", icon="help")
def _(page: mk.MkPage) -> None:
    page += mk.MkCommitConventions()

```

</details>

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
  source_filename: /home/runner/work/mknodes/mknodes/src/mknodes/manual/dev_section.py
  source_function: _
  source_line_no: 28
icon: material/help
title: Contributing

```

</details>

</details>
