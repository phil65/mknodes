# Site engines

## Site engines

The generator builds an engine-neutral output (pages, nav, assets, Markdown extensions,
template overrides) and a *writer* turns it into the input of a site engine. Choose the
engine with `--engine` (`mknodes build`, `serve`, `generate`). Each engine has a default
Markdown flavour, `--flavor` (or the `flavor` setting) overrides it.

| Engine | Default flavour | Config file | Build command | Needs |
| --- | --- | --- | --- | --- |
| `zensical` (default) | `material` | `mkdocs.generated.yml` (`INHERIT: mkdocs.yml`) | `zensical build -f mkdocs.generated.yml` | (installed with mknodes) |
| `mkdocs` | `material` | `mkdocs.generated.yml` (`INHERIT: mkdocs.yml`) | `mkdocs build -f mkdocs.generated.yml` | the `mkdocs` extra (`mknodes[mkdocs]`) |
| `mdbook` | `mdbook` | `book/book.toml` (+ `book/src/SUMMARY.md`) | `mdbook build book` | the [`mdbook`](https://rust-lang.github.io/mdBook/) binary on the `PATH` |
| `sphinx` | `myst` | `sphinx/conf.py` (+ toctrees in the pages) | `sphinx-build sphinx site` | the `sphinx` extra (`mknodes[sphinx]`) |
| `docsify` | `github` | `index.html` + `_sidebar.md` in the site folder | none (rendered in the browser) | nothing (Docsify comes from a CDN) |
| `markdown` | `github` | `SUMMARY.md` in the generated folder | none (the files are the result) | nothing |

``` bash
mknodes build --engine mkdocs
mknodes serve --engine mdbook
mknodes generate --engine mdbook   # works without mdBook installed
mknodes build --engine sphinx --strict   # sphinx-build -W --keep-going
mknodes serve --engine docsify     # static file server on http://localhost:3000/
```

### Zensical and MkDocs

Both read the same config: the generated pages go into the docs folder (hand-written files
are never overwritten) and `mkdocs.generated.yml` adds nav, extensions, CSS / JS and site
metadata on top of the project's `mkdocs.yml`. For MkDocs, the `mknodes` entry of the
`plugins` list (generator settings of former `mkdocs-mknodes` sites) gets dropped from the
generated config, since MkDocs can't load it. Page icons from Iconify are mapped to the
icons bundled with the theme or downloaded into the theme override folder.

### mdBook

The book folder (default `book/`, the `generated_dir` setting) is fully generated:
`book.toml`, `src/SUMMARY.md`, the pages and assets plus the hand-written files of the docs
folder. The HTML goes into the site dir (default `site/`). Additional `book.toml` content
comes from the `mdbook` setting:

``` toml
# pyproject.toml
[tool.mknodes.mdbook.output.html]
default-theme = "navy"
```

The `mdbook` flavour is the GitHub flavour (mdBook renders GitHub alerts, raw HTML and
`.md` links natively). Configure the
[`mdbook-admonish`](https://tommilligan.github.io/mdbook-admonish/) preprocessor
(`[tool.mknodes.mdbook.preprocessor.admonish]`) to get its fenced admonitions instead.
Note: `mdbook-admonish` 1.20 does not run with mdBook 0.5 (its preprocessor fails to parse
the book), so stay with the default alerts there.

The nav becomes `SUMMARY.md`: a section's index page becomes the section link, the
top-level index page the (unnumbered) intro chapter, sections without index page become
draft chapters. mdBook renders only pages listed there and every file only once, so
external links and duplicate entries are left out (pages missing from the nav get a warning).

### Sphinx (MyST)

The source folder (default `sphinx/`, the `generated_dir` setting) is fully generated:
`conf.py`, the pages in the `myst` flavour, assets and the hand-written files of the docs
folder (`.md` files are read by [MyST-Parser](https://myst-parser.readthedocs.io/), `.rst`
files work as well). The HTML goes into the site dir (default `site/`). Install the extra:
`pip install mknodes[sphinx]` (Sphinx, MyST-Parser, sphinx-design, Furo).

The `myst` flavour is the GitHub flavour with MyST directives in colon fences:
admonitions become `:::{note}` (with title: `:::{admonition} Title`), collapsible
admonitions and details blocks `:::{dropdown}` and tabs a `::::{tab-set}` of
`:::{tab-item}`s (both from [sphinx-design](https://sphinx-design.readthedocs.io/)), code
blocks with title / line numbers / highlighted lines a `{code-block}` with `:caption:`,
`:linenos:` and `:emphasize-lines:`. API docs are rendered from Griffe (no autodoc), their
anchors get MyST targets, so `[title][dotted.path]` references become links MyST checks.

Sphinx has no separate nav: the nav becomes `{toctree}` directives. The root `index.md`
gets one hidden toctree per top-level section (the section title as caption), section
index pages the toctree of their section; sections without index page get a generated
page (`_sections/`). A page may be in only one toctree, so duplicates are left out.

`conf.py` comes from the `sphinx` setting: `theme` (default `furo`), `extensions` (added
to `myst_parser` / `sphinx_design`); any other key becomes a `conf.py` variable:

``` toml
# pyproject.toml
[tool.mknodes.sphinx]
theme = "pydata_sphinx_theme"
extensions = ["sphinx.ext.intersphinx"]
html_theme_options = { navigation_depth = 2 }
```

`--strict` runs `sphinx-build -W --keep-going`. Some warnings are suppressed by default
(`suppress_warnings`): unknown Pygments lexers (`mermaid`), pages outside the nav,
non-consecutive heading levels, duplicate link definitions and unreferenced footnotes,
which Python-Markdown accepts as well.

[Jupyter Book 2](https://next.jupyterbook.org/) reads the same MyST Markdown (its
`myst.yml` instead of `conf.py` and toctrees), so a writer for it would reuse the `myst`
flavour. [Quarto](https://quarto.org/) is close as well: Pandoc's fenced divs
(`::: {.callout-note}`, `::: {.panel-tabset}`) instead of MyST directives.

### Docsify

[Docsify](https://docsify.js.org/) renders Markdown in the browser, so there is no build
step: the site folder (the site dir, default `site/`; for `generate` the
`generated_dir`) holds `index.html` (Docsify 5 and its search plugin from a CDN, pinned),
`_sidebar.md` (the nav), the pages in the GitHub flavour (Docsify 5 renders GitHub
alerts), assets and the hand-written files of the docs folder. `serve` runs a static file
server. Extra `window.$docsify` options come from the `docsify` setting
(`[tool.mknodes.docsify]`, e.g. `themeColor`).

### What degrades outside Material

The `docsify` engine renders the `github` flavour, so it degrades like it.

| Feature | `github` / `mdbook` flavour (also Docsify) | with `mdbook-admonish` | `myst` flavour (Sphinx) |
| --- | --- | --- | --- |
| Admonitions (`!!!`, `MkAdmonition`) | GitHub alerts (5 types), collapsible ones as `<details>`, nested ones as quotes with a bold title | all Material types, titles, collapsible | docutils admonitions (10 types), titles, nesting; collapsible ones as sphinx-design dropdowns |
| Content tabs (`===`, `MkTabbed`) | one `<details>` block per tab, the selected one open | same | sphinx-design tab sets (empty tabs left out) |
| PyMdown blocks (`/// details`) | `<details>` / alerts, other blocks keep their content | admonitions | dropdowns / admonitions, other blocks keep their content |
| Code blocks | plain language info string, the title as bold line above, no line numbers / highlighted lines | same | `{code-block}` with caption, line numbers, highlighted lines |
| API docs (`:::`, `MkDocStrings`) | rendered from Griffe (no mkdocstrings) | same | same (no autodoc) |
| `[title][dotted.path]` references | linked to the anchors of the rendered API docs / inventories | same | same, checked by MyST (targets) |
| Icons (`MkIcon`, link icons) | Iconify `<img>` (needs network access when viewing) | same | same |
| Badges (`MkBadge`, inline SVG) | static shields.io badge images (GitHub drops inline SVG) | same | same |
| Mermaid diagrams | code blocks (GitHub renders them, mdBook needs `mdbook-mermaid`, Docsify a plugin) | same | code blocks (needs `sphinxcontrib-mermaid`) |
| Grids, cards, speech bubbles, ... (Material CSS) | plain HTML / Markdown without Material's styling | same | same |
| Attribute lists, code annotations, theme templates | dropped | same | same |
| Page metadata (front matter) | a `# Title` heading only | same | same |
| Navigation | `SUMMARY.md` (mdBook), `_sidebar.md` (Docsify) | same | toctrees, a page only once |

<details>
<summary>Page info</summary>

<details>
<summary>Code for this page</summary>

**mknodes.manual.site._**

```python
@nav.route.page("Site engines", hide="toc")
def _(page: mk.MkPage):
    page += mk.MkTemplate("site/engines.jinja")

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
  source_filename: /home/runner/work/mknodes/mknodes/src/mknodes/manual/site/__init__.py
  source_function: _
  source_line_no: 34
hide:
- toc
title: Site engines

```

</details>

</details>
