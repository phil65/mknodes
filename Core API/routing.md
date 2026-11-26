# Routing

Instead of adding pages imperatively, functions can get registered for a nav path.
`nav.route` is a [NavRouter](#mknodes.navs.navrouter.NavRouter) bound to the nav,
[Router](#mknodes.Router) collects routes without a nav (for example in a module which
gets imported by several build functions) and attaches them via `register_nodes(nav)`.
The [MkNavs / Using decorators](<../MkNavs/Using decorators/index.md>) section is built this way.

**Example**

```py
import mknodes as mk

nav = mk.MkNav("Guides")


@nav.route.page("First steps", icon="rocket")
def _(page: mk.MkPage):
    page += "Some text"


@nav.route.nav("Advanced")
def _(nav: mk.MkNav):
    nav.add_page("Plugins")
```

## <a id="mknodes.Router"></a>`mknodes.Router`

```python
class Router
```

Class used for MkNav decorator routing.

## <a id="mknodes.navs.navrouter.NavRouter"></a>`mknodes.navs.navrouter.NavRouter`

```python
class NavRouter
```

Class used for MkNav decorator routing.

### <a id="mknodes.navs.navrouter.NavRouter.__call__"></a>`__call__`

```python
def __call__(*path: str) -> Callable[[AnyNavSubTypeCallable], Any]
```

Decorator method to use for routing.

The decorated functions need to return either a MkPage or an MkNav.
They will get registered to the router-MkNav then.

In comparison to `page()` and `nav()`, it is not required to know in advance what
will be returned.

**Parameters:**

| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `path` | `str` | The section path for the returned `MkNav` / `MkPage` | () |

### <a id="mknodes.navs.navrouter.NavRouter.__init__"></a>`__init__`

```python
def __init__(nav: mknav.MkNav) -> None
```

Constructor.

**Parameters:**

| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `nav` | `mknav.MkNav` | MkNav to use for routing |  |

### <a id="mknodes.navs.navrouter.NavRouter.nav"></a>`nav`

```python
def nav(*path: str, **kwargs: Any) -> Callable[[AnyNavCallable], Any]
```

Decorator method to use for routing Navs.

The decorated functions will get passed an MkNav as an argument which can be
modified then.
They will get registered to the router-MkNav afterwards.

There is also the possibility to create a new MkNav and return it in the
decorated method, that MkNav takes preference then over the modified one.

**Examples:**

``` py
@nav.route.nav("Routed nav")
def _(nav: mk.MkNav):
    nav += ...
```

**Parameters:**

| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `path` | `str` | The section path for the returned MkNav | () |
| `kwargs` | `Any` | Keyword arguments passed to the MkNav constructor. | {} |

### <a id="mknodes.navs.navrouter.NavRouter.page"></a>`page`

```python
def page(*path: str, **kwargs: Any) -> Callable[[AnyPageCallable], Any]
```

Decorator method to use for routing Pages.

The decorated functions will get passed an MkPage as an argument which can be
modified then.
The resulting page will get registered to the router-MkNav afterwards.

There is also the possibility to create a new MkPage and return it in the
decorated method, that MkPage takes preference then over the modified one.

The keyword arguments can be used to pass metadata-related keyword arguments
to the MkPage constructor.

**Examples:**

``` py
@nav.route.page("Routed page", icon=...)
def _(page: mk.MkPage):
    page += ...
```

Args:
    path: The section path for the returned MkPage
    kwargs: Keyword arguments passed to the MkPage constructor.

<details>
<summary>Page info</summary>

<details>
<summary>Code for this page</summary>

**mknodes.manual.api_section._add_page.<locals>._**

```python
@nav.route.page(title, hide="toc")
def _(page: mk.MkPage) -> None:
    page += INTROS[title]
    page += mk.MkCode(EXAMPLES[title].rstrip(), language="py", title="Example")
    for identifier in identifiers:
        page += mk.MkDocStrings(identifier, **DOCSTRING_OPTIONS)

```

</details>

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
  source_filename: /home/runner/work/mknodes/mknodes/src/mknodes/manual/api_section.py
  source_function: _add_page.<locals>._
  source_line_no: 168
hide:
- toc
title: Routing

```

</details>

</details>
