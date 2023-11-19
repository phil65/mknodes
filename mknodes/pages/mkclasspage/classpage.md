{% block content %}

{% if subclasses %}
{{ "Sub classes" | MkHeader(level=3) }}
{{ subclasses | MkClassTable }}
{% endif %}

{% if cls.mro() | length > 2 %}
{{ "Base classes" | MkHeader(level=3) }}
{{ cls.__bases__ | MkClassTable }}
{{ "⋔ Inheritance diagram" | MkHeader(level=3) }}
{{ cls | MkClassDiagram(mode="baseclasses") }}
{% endif %}

{{ "🛈 DocStrings" | MkHeader(level=3) }}

{{ cls | MkDocStrings }}

{% if github_url %}
{{ github_url | MkLink(title="Show source on GitHub", icon="fa-brands:github") }}
{% endif %}

{% endblock %}
