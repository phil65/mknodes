# Using decorators

## Code for this section

**routing.py**

```py
"""MkNodes routing example.

MkNodes also supports setting up Navs via decorators.
"""

import mknodes as mk


NAV_TEXT = """You can also use decorators to attach MkNavs. These navs then can continue
to build the tree without using decorators (by adding sub-navs).
"""

nav = mk.MkNav("Using decorators")


@nav.route.page("Routed page")
def routed_page(page: mk.MkPage) -> None:
    """Builds a MkPage and attaches it to the router MkNav."""
    page += mk.MkAdmonition("I'm a page added via decorators!")


@nav.route.page("Routed", "Deeply", "Nested", "Nested page")
def routed_nested_page(page: mk.MkPage) -> None:
    """Builds a nested MkPage and attaches it to the router MkNav."""
    page += mk.MkAdmonition("I'm a nested page added via decorators!")


@nav.route.nav("Routed", "Deeply", "Nested", "Nav")
def routed_nav(nav: mk.MkNav) -> None:
    """Builds a nested MkNav and attaches it to the router MkNav."""
    index_page = nav.add_page(is_index=True)
    index_page += mk.MkAdmonition(NAV_TEXT)
    page = nav.add_page("Routed section page")
    page += mk.MkAdmonition("Routed section page content")

```

## MkNav.route Docstrings

<a id="mknodes.navs.navrouter.NavRouter"></a>

```python
class NavRouter
```

Class used for MkNav decorator routing.

## <a id="mknodes.navs.navrouter.NavRouter.__call__"></a>`__call__`

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

## <a id="mknodes.navs.navrouter.NavRouter.__init__"></a>`__init__`

```python
def __init__(nav: mknav.MkNav) -> None
```

Constructor.

**Parameters:**

| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `nav` | `mknav.MkNav` | MkNav to use for routing |  |

## <a id="mknodes.navs.navrouter.NavRouter.nav"></a>`nav`

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

## <a id="mknodes.navs.navrouter.NavRouter.page"></a>`page`

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
<summary>Code for this section</summary>

**mknodes.manual.navs_section._**

```python
@nav.route.nav("Routing")
def _(nav: mk.MkNav) -> mk.MkNav:
    page = routing.nav.add_page(is_index=True, icon="material/call-split", hide="toc")
    page += mk.MkCode.for_file(routing.__file__, header="Code for this section")
    page += mk.MkDocStrings(navrouter.NavRouter, header="MkNav.route Docstrings")
    return routing.nav

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
  source_filename: /home/runner/work/mknodes/mknodes/src/mknodes/manual/navs_section.py
  source_function: _
  source_line_no: 43
hide:
- toc
icon: material/call-split
title: Using decorators

```

</details>

</details>
