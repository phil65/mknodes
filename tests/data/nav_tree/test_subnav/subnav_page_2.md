## Code for this page

``` py
def create_static_page(nav: mknav.MkNav):
    pass  # statically loaded page, nothing to see here
```


Finally a break to write some **regular** markdown!


## What is MkNodes

* Markdown objectified. A complete `MkDocs` project can be built by attaching nodes
  to a tree. Nodes range from atomic Markdown elements up to composed templates.

* A parametrized Webpage. Because the tree only gets evaluted when it is written,
  it can basically behave like a template. Changing the project connected to the
  tree also changes the content of Nodes which pull metadata from the project.

* `MkNodes` is aligned to the popular MkDocs/MkDocstrings/MkDocs for Material/PyMDown
  documentation stack for python. Other themes work probably, too, but are not tested.

* It is *not* a parser. The only things that get parsed are SUMMARY.md files and the
  Markdown page metadata, for the rest it´s a one-way street: Python-objects -> Markdown.

## Why MkNodes?

* Because it´s fun! Especially for people who dont like working with Markdown, this
  library enables to build great documentation webpages without writing a single line
  of markdown, and without having to deal with the actual Directory structure at all.

* Dead simple API: Basically all that is needed is initializing nodes and appending them to
  the tree (by using `+=`. All nodes are available from the `mknodes` namespace.

* Because it´s reusable. Large parts of the documentation can be written in a project-agnostic way (because the nodes are populated with metadata dynamically).

* Especially generating more complex, nested Markdown is much more comfortable.


## Use cases

**MkNodes** can be used in many different ways

* Create complete websites
    * **MkNodes** can be used to create the complete website (like it is done with this page)

* Load existing websites and extend it
    * By using `MkNav.from_folder` / `from_file` as well as `MkPage.from_file`,
      the existing Markdown pages can become part of our tree
      (which we can extend programatically)

* Create a subsection with **MkNodes** and reference it from your "static" page.
    * You can also set a section name for your root `MkNav` and reference that from your
      `nav:` section in mkdocs.yml

* Create single static pages / blocks for your page
    You can also just use **MkNodes** to create some Nodes, stringify them and include
    the markdown in your static pages

* Using `Markdown-Exec` or similar inline execution plugins
    You can also embed **MkNodes** code directly by using various plug-ins
    (personal recommendation: `Markdown-Exec`)
