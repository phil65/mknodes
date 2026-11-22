## Class info

{% if klasses %}
### Classes

{{ klasses | MkClassTable }}
{% endif %}

{% if reexported %}
### Re-exported classes

{{ reexported | MkClassTable(layout="compact") }}
{% endif %}

### 🛈 DocStrings

{{ module | MkDocStrings }}
