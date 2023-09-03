## Plugin requirements

### Files
All files conneted to the node tree:
````` py
{{ files.keys() | list | pprint | indent(4, first=True) }}
`````

### Plugins
Standard MkDocs configuration information. Do not try to modify.

````` py
{{ plugins | pprint | indent(4, first=True) }}
`````

### CSS
Standard MkDocs configuration information. Do not try to modify.

````` css
{{ css | indent(4, first=True) }}
`````

### Markdown extensions
Extensions used by the tree nodes:

````` py
{{ markdown_extensions | pprint | indent(4, first=True) }}
`````
