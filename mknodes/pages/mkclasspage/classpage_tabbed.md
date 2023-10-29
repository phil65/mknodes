{% block content %}

=== "DocStrings"
{{ cls | MkDocStrings | str | indent(first=True) }}

{% if subclasses %}
=== "Sub classes"
{{ subclasses | MkClassTable | str | indent(first=True) }}
{% endif %}

{% if cls.mro() | length > 2 %}
=== "Base classes"
{{ cls.__bases__ | MkClassTable | str | indent(first=True) }}
=== "⋔ Inheritance diagram"
{{ cls | MkClassDiagram(mode="baseclasses") | str | indent(first=True) }}
{% endif %}

{% endblock %}
