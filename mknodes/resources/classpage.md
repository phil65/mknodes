{% block content %}

{% if subclasses %}
### Sub classes
{{ subclasses | MkClassTable }}
{% endif %}

{% if cls.mro() | length > 2 %}
### Base classes
{{ cls.__bases__ | MkClassTable }}
### ⋔ Inheritance diagram
{{ cls | MkClassDiagram(mode="baseclasses") }}
{% endif %}

### 🛈 DocStrings

{{ cls | MkDocStrings }}

{% endblock %}
