# The build process

This section provides an overview about the sequence of operations applied by **MkNodes** when running the full build process.

<section class="timeline">
<div class="timeline-item">
<div class="timeline-img"></div>
<div class="timeline-content js--fadeInLeft">
<div class="date">Step 1</div>
<p>
<h3 id="load-settings">Load settings<a href="#load-settings" aria-label="Link to heading 'Load settings'" data-heading-content="Load settings" class="anchor"></a>
</h3>
<p>Settings are read from the <code>mknodes</code> entry of the <code>plugins</code> list in <code>mkdocs.yml</code>,
<code>[tool.mknodes]</code> in <code>pyproject.toml</code> and the CLI options. The target repository gets
cloned in case it is a remote one.</p>
</p>
</div>
</div>
<div class="timeline-item">
<div class="timeline-img"></div>
<div class="timeline-content js--fadeInRight">
<div class="date">Step 2</div>
<p>
<h3 id="create-theme">Create theme<a href="#create-theme" aria-label="Link to heading 'Create theme'" data-heading-content="Create theme" class="anchor"></a>
</h3>
<p>Initialize the theme object based on the theme configured in <code>mkdocs.yml</code>
(default: <code>material</code>).</p>
</p>
</div>
</div>
<div class="timeline-item">
<div class="timeline-img"></div>
<div class="timeline-content js--fadeInLeft">
<div class="date">Step 3</div>
<p>
<h3 id="create-context">Create context<a href="#create-context" aria-label="Link to heading 'Create context'" data-heading-content="Create context" class="anchor"></a>
</h3>
<p>All available information from following sources is extracted in order to build
a project context:</p>
<ul>
<li>metadata.Distribution</li>
<li>PyProject File</li>
<li>Site config file (<code>mkdocs.yml</code>)</li>
<li>Other config files in the repository</li>
<li>Git repository info</li>
<li>Information from GitHub</li>
</ul>
</p>
</div>
</div>
<div class="timeline-item">
<div class="timeline-img"></div>
<div class="timeline-content js--fadeInRight">
<div class="date">Step 4</div>
<p>
<h3 id="build-mknodes-tree">Build <strong>MkNodes</strong> tree<a href="#build-mknodes-tree" aria-label="Link to heading 'Build MkNodes tree'" data-heading-content="Build MkNodes tree" class="anchor"></a>
</h3>
<p>The build function (<code>build_fn</code>) is executed with the root <code>MkNav</code> and the theme
and the node tree is generated. Without any configuration, the default build function
creates a default website (README, API docs, CLI docs, development pages).</p>
</p>
</div>
</div>
<div class="timeline-item">
<div class="timeline-img"></div>
<div class="timeline-content js--fadeInLeft">
<div class="date">Step 5</div>
<p>
<h3 id="collect-build-artifacts">Collect build artifacts<a href="#collect-build-artifacts" aria-label="Link to heading 'Collect build artifacts'" data-heading-content="Collect build artifacts" class="anchor"></a>
</h3>
<p>MkNodes' <code>DocBuilder</code> walks the node tree and renders every page in the Markdown
flavour of the engine (<code>material</code> for Zensical, <code>github</code> for plain Markdown), incl.
front matter, rendered with <strong>jinja2</strong>. It aggregates the required resources
(CSS / JS / Markdown extensions) and the page templates and converts the template
blocks to HTML. The result is an engine-neutral <code>BuildOutput</code>.</p>
</p>
</div>
</div>
<div class="timeline-item">
<div class="timeline-img"></div>
<div class="timeline-content js--fadeInRight">
<div class="date">Step 6</div>
<p>
<h3 id="write-the-site-input">Write the site input<a href="#write-the-site-input" aria-label="Link to heading 'Write the site input'" data-heading-content="Write the site input" class="anchor"></a>
</h3>
<p>A writer turns the <code>BuildOutput</code> into the engine input. The <code>ZensicalWriter</code> writes the
pages and assets into the docs folder and the
template overrides into the theme <code>custom_dir</code> (both tracked in a generated
<code>.gitignore</code>, hand-written files are never overwritten) as well as
<code>mkdocs.generated.yml</code>, which inherits from <code>mkdocs.yml</code> and adds the nav,
the Markdown extensions and the extra CSS / JS.</p>
</p>
</div>
</div>
<div class="timeline-item">
<div class="timeline-img"></div>
<div class="timeline-content js--fadeInLeft">
<div class="date">Step 7</div>
<p>
<h3 id="build-with-zensical">Build with <strong>Zensical</strong>
<a href="#build-with-zensical" aria-label="Link to heading 'Build with Zensical'" data-heading-content="Build with Zensical" class="anchor"></a>
</h3>
<p>
<code>zensical build -f mkdocs.generated.yml</code> renders the website.</p>
</p>
</div>
</div>
</section>

<details>
<summary>Page info</summary>

<details>
<summary>Code for this page</summary>

**mknodes.manual.site._**

```python
@nav.route.page("The build process", hide="toc")
def _(page: mk.MkPage):
    page += INTRO
    page += mk.MkTimeline(paths.RESOURCES / "timeline_data.toml")

```

</details>

<details>
<summary>Resources</summary>

```python
Resources(css=[],
          markdown_extensions={},
          plugins=[],
          js=[],
          assets=[Asset('scrollreveal_cab73ad.js'),
                  Asset('timeline_577131c.js'),
                  Asset('timeline_63b66a4.css')],
          packages=[])
```

</details>

<details>
<summary>Metadata</summary>

```yaml
created:
  source_filename: /home/runner/work/mknodes/mknodes/src/mknodes/manual/site/__init__.py
  source_function: _
  source_line_no: 39
hide:
- toc
title: The build process

```

</details>

</details>
