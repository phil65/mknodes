## Plugin requirements

### Files

All files connected to the node tree:

{{ filenames | MkPrettyPrint }}

### Plugins

Plugins used by the tree nodes:

{{ plugins | MkPrettyPrint }}

### CSS

CSS used by the tree nodes:

{% for filename, content in css.items() %}

{{ filename | MkHeader(level=4)}}

{{ content | MkCode(language="css") }}

{% endfor %}

### Markdown extensions

Extensions used by the tree nodes:

{{ markdown_extensions | dump_yaml |  MkCode(language="yaml") }}
