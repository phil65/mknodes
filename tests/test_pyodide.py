import pytest

from mknodes.basenodes import mkpyodide
from mknodes.utils import resources


def test_default_pyodide_version_and_url() -> None:
    expected_url = "https://cdn.jsdelivr.net/pyodide/v314.0.8/full/pyodide.js"
    assert mkpyodide.PYODIDE_VERSION == "314.0.8"
    assert expected_url == mkpyodide.PYODIDE_JS
    assert mkpyodide.pyodide_js_url() == expected_url


def test_metadata_and_node_pyodide_url_agree() -> None:
    nodefile = mkpyodide.MkPyodideTerminal.get_nodefile()
    assert nodefile is not None
    metadata_pyodide_links = [
        js.link for js in nodefile.js if isinstance(js, resources.JSFile) and "pyodide" in js.link
    ]
    node_pyodide_links = [
        js.link
        for js in mkpyodide.MkPyodideTerminal.JS_FILES
        if isinstance(js, resources.JSFile) and "pyodide" in js.link
    ]
    assert metadata_pyodide_links == [mkpyodide.PYODIDE_JS]
    assert node_pyodide_links == [mkpyodide.PYODIDE_JS]
    assert metadata_pyodide_links == node_pyodide_links


def test_default_terminal_uses_default_pyodide_version() -> None:
    terminal = mkpyodide.MkPyodideTerminal("print('hello')")
    assert terminal.pyodide_version == mkpyodide.PYODIDE_VERSION

    node_resources = terminal.get_resources_sync()
    js_links = [js.link for js in node_resources.js if isinstance(js, resources.JSFile)]
    assert mkpyodide.PYODIDE_JS in js_links

    content = terminal.get_content()
    content_js_links = [js.link for js in content.resources.js if isinstance(js, resources.JSFile)]
    assert mkpyodide.PYODIDE_JS in content_js_links


def test_custom_pyodide_version() -> None:
    custom_version = "0.27.2"
    expected_url = mkpyodide.pyodide_js_url(custom_version)
    terminal = mkpyodide.MkPyodideTerminal("print('hello')", pyodide_version=custom_version)

    assert terminal.pyodide_version == custom_version

    node_resources = terminal.get_resources_sync()
    js_links = [js.link for js in node_resources.js if isinstance(js, resources.JSFile)]
    assert expected_url in js_links
    assert mkpyodide.PYODIDE_JS not in js_links

    content = terminal.get_content()
    content_js_links = [js.link for js in content.resources.js if isinstance(js, resources.JSFile)]
    assert expected_url in content_js_links
    assert mkpyodide.PYODIDE_JS not in content_js_links


if __name__ == "__main__":
    pytest.main([__file__])
