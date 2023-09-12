## Plugin requirements

### Files

All files connected to the node tree:

{{ page_mapping | MkPrettyPrint }}

### Plugins

Plugins used by the tree nodes:

{{ requirements.plugins | MkPrettyPrint }}

### CSS

CSS used by the tree nodes:

{% for filename, content in requirements.css.items() %}

{{ filename | MkHeader(level=4)}}

{{ content | MkCode(language="css") }}

{% endfor %}

### Markdown extensions

Extensions used by the tree nodes:

{{ requirements.markdown_extensions | dump_yaml |  MkCode(language="yaml") }}
