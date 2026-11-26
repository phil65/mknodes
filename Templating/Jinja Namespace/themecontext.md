# ThemeContext

<a id="mknodes.info.contexts.ThemeContext"></a>

```python
class ThemeContext
```

Information about the theme.

#### <a id="mknodes.info.contexts.ThemeContext.admonitions"></a>`admonitions`

```python
admonitions: list[Any] = dataclasses.field(default_factory=list)
```

#### <a id="mknodes.info.contexts.ThemeContext.css_accent_bg"></a>`css_accent_bg`

```python
css_accent_bg: str = ''
```

#### <a id="mknodes.info.contexts.ThemeContext.css_accent_fg"></a>`css_accent_fg`

```python
css_accent_fg: str = ''
```

#### <a id="mknodes.info.contexts.ThemeContext.css_accent_fg_transparent"></a>`css_accent_fg_transparent`

```python
css_accent_fg_transparent: str = ''
```

#### <a id="mknodes.info.contexts.ThemeContext.css_default_bg"></a>`css_default_bg`

```python
css_default_bg: str = ''
```

#### <a id="mknodes.info.contexts.ThemeContext.css_default_fg"></a>`css_default_fg`

```python
css_default_fg: str = ''
```

#### <a id="mknodes.info.contexts.ThemeContext.css_primary_bg"></a>`css_primary_bg`

```python
css_primary_bg: str = ''
```

#### <a id="mknodes.info.contexts.ThemeContext.css_primary_bg_light"></a>`css_primary_bg_light`

```python
css_primary_bg_light: str = ''
```

#### <a id="mknodes.info.contexts.ThemeContext.css_primary_fg"></a>`css_primary_fg`

```python
css_primary_fg: str = ''
```

#### <a id="mknodes.info.contexts.ThemeContext.data"></a>`data`

```python
data: dict[str, str] = dataclasses.field(default_factory=dict)
```

Additional data of the theme.

#### <a id="mknodes.info.contexts.ThemeContext.name"></a>`name`

```python
name: str = ''
```

Name of the theme.

#### <a id="mknodes.info.contexts.ThemeContext.primary_color"></a>`primary_color`

```python
primary_color: str = ''
```

Primary color.

#### <a id="mknodes.info.contexts.ThemeContext.text_color"></a>`text_color`

```python
text_color: str = ''
```

Primary text color.

#### <a id="mknodes.info.contexts.ThemeContext.__init__"></a>`__init__`

```python
def __init__(name: str = '', primary_color: str = '', text_color: str = '', data: dict[str, str] = dict(), admonitions: list[Any] = list(), css_primary_fg: str = '', css_primary_bg: str = '', css_primary_bg_light: str = '', css_accent_fg: str = '', css_accent_fg_transparent: str = '', css_accent_bg: str = '', css_default_fg: str = '', css_default_bg: str = '') -> None
```

#### <a id="mknodes.info.contexts.ThemeContext.__repr__"></a>`__repr__`

```python
def __repr__() -> str
```

<details>
<summary>Page info</summary>

<details>
<summary>Resources</summary>

```python
Resources(css=[],
          markdown_extensions={},
          plugins=[],
          js=[],
          assets=[],
          packages=[])
```

</details>

<details>
<summary>Metadata</summary>

```yaml
created:
  source_filename: /home/runner/work/mknodes/mknodes/src/mknodes/manual/templating_section.py
  source_function: _
  source_line_no: 42
title: ThemeContext

```

</details>

</details>
