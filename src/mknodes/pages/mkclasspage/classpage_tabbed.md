{% block content %}
=== "DocStrings"
{{ (obj_path or cls) | MkDocStrings | string | indent(first=True) }}

{% if subclasses %}
=== "Sub classes"
{{ subclasses | MkClassTable | string | indent(first=True) }}
{% endif %}

{% if cls.mro() | length > 2 %}
=== "Base classes"
{{ cls.__bases__ | MkClassTable | string | indent(first=True) }}
=== "⋔ Inheritance diagram"
{{ cls | MkClassDiagram(mode="baseclasses") | string | indent(first=True) }}
{% endif %}

{% if github_url %}
{{ github_url | MkLink(title="Show source on GitHub", icon="fa-brands:github") }}
{% endif %}

{% endblock %}
