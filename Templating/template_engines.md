# Template engines

MkNodes renders its Jinja templates (node files, `MkTemplate`, `render_jinja` texts, the
Jinja pass of generated pages) with **Jinja2** by default. **minijinja**, a Rust
implementation of Jinja, can be used instead:

```bash
pip install "mknodes[minijinja]"
mknodes build --jinja-engine minijinja
```

The engine comes from (first one set wins):

1. the CLI option `--jinja-engine` of `build`, `serve` and `generate`,
2. `jinja-engine = "minijinja"` in `[tool.mknodes]` of `pyproject.toml` (or the `mknodes`
   entry in the plugins list of `mkdocs.yml`),
3. the environment variable `MKNODES_JINJA_ENGINE` (also used by nodes created outside
   a site build, e.g. in tests),
4. `jinja2`.

Both engines come from [jinjarope](https://phil65.github.io/jinjarope/template_engines/),
which lists the differences. All filters, globals and node classes are the same; templates
of MkNodes itself render the same with both. What to watch for in your own templates:

- Attributes starting with `_` are hidden from `obj.attr`: use the `getattr` filter
  (`{{ cls | getattr("__name__") }}`), it works with both engines.
- `mapping.key(...)` calls a method: mappings need a `__getattr__` (`mk.MkText(...)`,
  `_mk.MkText(...)` work).
- Strings are minijinja strings with a subset of Python's `str` methods (no
  `removesuffix`: use the filter of the same name); `"%s" % x` is not supported.
- Node metadata (`created.source_filename`) of nodes created in templates points to the
  Python code that rendered the template (templates have no Python frames).

<details>
<summary>Page info</summary>

<details>
<summary>Code for this page</summary>

**mknodes.manual.templating_section._**

```python
@nav.route.page("Template engines")
def _(page: mk.MkPage) -> None:
    page += mk.MkTemplate("templating/template_engines.jinja")

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
  source_filename: /home/runner/work/mknodes/mknodes/src/mknodes/manual/templating_section.py
  source_function: _
  source_line_no: 60
title: Template engines

```

</details>

</details>
