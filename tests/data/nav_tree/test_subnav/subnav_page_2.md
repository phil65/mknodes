## Code for this page

``` py
def create_static_page(nav: mknav.MkNav):
    pass  # statically loaded page, nothing to see here
```


Finally a break to write some **regular** markdown!

## Use cases

MkNodes can be used in many different ways

* Create complete websites
    * MkNodes can be used to create the complete website (like it is done with this page)

* Load existing websites and extend it
    * By using MkNav.from_folder / from_file as well as MkPage.from_file,
      the existing Markdown pages can become part of our tree
      (which we can extend programatically)

* Create a subsection with MkNodes and reference it from your "static" page.
    * You can also set a section name for your root MkNav and reference that from your
      `nav:` section in mkdocs.yml

* Create single static pages / blocks for your page
    You can also just use MkNodes to create some Nodes, stringify them and include
    the markdown in your static pages

* Using Markdown-Exec or similar inline execution plugins
    You can also embed MkNodes code directly by using various plug-ins
    (personal recommendation: Markdown-Exec)
