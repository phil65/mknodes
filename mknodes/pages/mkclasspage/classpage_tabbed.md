{% block content %}

{{ github_url | MkLink(title="Show source on GitHub", icon="fa-brands:github", as_button=True) }}

=== "DocStrings"
{{ cls | MkDocStrings | string | indent(first=True) }}

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

{% endblock %}
