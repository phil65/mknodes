from __future__ import annotations

from collections.abc import MutableMapping
import pathlib
import sys
import textwrap

import pytest

import mknodes as mk
from mknodes.navs import apiscope


PKG = "apidocpkg"

FILES = {
    "__init__.py": """
        from apidocpkg.schema import Schema
        from apidocpkg._impl import Hidden
        from apidocpkg.sub import Foo

        __all__ = ["Defined", "Foo", "Hidden", "Schema"]


        class Defined:
            pass
    """,
    "__main__.py": "raise SystemExit('__main__ must not be imported')\n",
    "schema.py": """
        class Schema:
            pass


        class SchemaHelper(Schema):
            pass
    """,
    "_impl.py": """
        class Hidden:
            pass


        class Orphan:
            pass
    """,
    "config/__init__.py": """
        class Config:
            pass
    """,
    "config/config.py": """
        from apidocpkg.config import Config


        class Other(Config):
            pass
    """,
    "sub/__init__.py": """
        from apidocpkg.sub.impl import Foo

        __all__ = ["Foo"]
    """,
    "sub/impl.py": """
        from apidocpkg.schema import Schema


        class Foo(Schema):
            pass
    """,
    "sub/_private.py": """
        class SubOrphan:
            pass
    """,
    "abcstyle/__init__.py": """
        from apidocpkg.abcstyle._defs import *  # noqa: F403

        __all__ = ["Facade"]
    """,
    "abcstyle/_defs.py": """
        class Facade:
            pass


        Facade.__module__ = "apidocpkg.abcstyle"
    """,
}


@pytest.fixture(scope="module")
def pkg(tmp_path_factory):
    root = tmp_path_factory.mktemp("apidoc")
    for rel_path, content in FILES.items():
        path = root / PKG / rel_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(textwrap.dedent(content).lstrip())
    sys.path.insert(0, str(root))
    yield PKG
    sys.path.remove(str(root))


def _build(pkg: str, **kwargs) -> mk.MkDoc:
    nav = mk.MkNav()
    return nav.add_doc(pkg, section_name="API", **kwargs)


def _iter_pages(nav: mk.MkNav):
    for _level, node in nav.iter_nodes():
        if isinstance(node, mk.MkPage):
            yield node


def _page_url(path: str) -> str:
    p = pathlib.PurePosixPath(path)
    if p.name in {"index.md", "README.md"}:
        return f"{p.parent.as_posix()}/"
    return f"{p.with_suffix('').as_posix()}/"


def _class_pages(doc: mk.MkDoc) -> dict[str, str]:
    return {
        apiscope.class_path(p.klass): p.resolved_file_path
        for p in _iter_pages(doc)
        if isinstance(p, mk.MkClassPage)
    }


def test_scope_homes(pkg):
    module = __import__(pkg)
    scope = apiscope.ApiScope.build(module, recursive=True)
    homes = {k.__name__: home for k, home in scope.homes.items()}
    assert homes == {
        "Defined": "apidocpkg",
        "Schema": "apidocpkg.schema",
        "SchemaHelper": "apidocpkg.schema",
        "Hidden": "apidocpkg",  # private module, re-exported publicly
        "Orphan": "apidocpkg",  # private module, not re-exported: nearest public parent
        "Foo": "apidocpkg.sub.impl",
        "SubOrphan": "apidocpkg.sub",
        "Config": "apidocpkg.config",
        "Other": "apidocpkg.config.config",
        "Facade": "apidocpkg.abcstyle",  # __module__ points to the public facade
    }
    assert not [m for m in scope.modules if "._" in m or m.endswith("__main__")]
    reexported = [k.__name__ for k in scope.reexports_for("apidocpkg")]
    assert reexported == ["Foo", "Schema"]
    assert [k.__name__ for k in scope.reexports_for("apidocpkg.sub")] == ["Foo"]


def test_recursive_url_scheme(pkg):
    doc = _build(pkg, recursive=True)
    pages = _class_pages(doc)
    assert pages == {
        "apidocpkg.Defined": "API/Defined.md",
        "apidocpkg._impl.Hidden": "API/Hidden.md",
        "apidocpkg._impl.Orphan": "API/Orphan.md",
        "apidocpkg.schema.Schema": "API/schema/Schema.md",
        "apidocpkg.schema.SchemaHelper": "API/schema/SchemaHelper.md",
        "apidocpkg.sub.impl.Foo": "API/sub/impl/Foo.md",
        "apidocpkg.sub._private.SubOrphan": "API/sub/SubOrphan.md",
        # class clashes (case-insensitively) with submodule `config.config`
        "apidocpkg.config.Config": "API/config/Config-class.md",
        "apidocpkg.config.config.Other": "API/config/config/Other.md",
        "apidocpkg.abcstyle.Facade": "API/abcstyle/Facade.md",
    }
    module_pages = {
        p.module.__name__: p.resolved_file_path
        for p in _iter_pages(doc)
        if isinstance(p, mk.MkModulePage)
    }
    assert module_pages == {
        "apidocpkg": "API/index.md",
        "apidocpkg.schema": "API/schema/index.md",
        "apidocpkg.sub": "API/sub/index.md",
        "apidocpkg.sub.impl": "API/sub/impl/index.md",
        "apidocpkg.config": "API/config/index.md",
        "apidocpkg.config.config": "API/config/config/index.md",
        "apidocpkg.abcstyle": "API/abcstyle/index.md",
    }


def test_every_class_appears_once(pkg):
    doc = _build(pkg, recursive=True)
    klasses = [p.klass for p in _iter_pages(doc) if isinstance(p, mk.MkClassPage)]
    assert len(klasses) == len(set(klasses))


def test_urls_are_collision_free(pkg):
    doc = _build(pkg, recursive=True)
    urls = [_page_url(p.resolved_file_path) for p in _iter_pages(doc)]
    assert len(urls) == len(set(urls))
    lowered = [u.lower() for u in urls]  # case-insensitive file systems
    assert len(lowered) == len(set(lowered))


def test_unique_page_name():
    taken = {"index", "config"}
    assert apiscope.unique_page_name("Config", taken) == "Config-class"
    assert apiscope.unique_page_name("CONFIG", taken) == "CONFIG-class-2"
    assert apiscope.unique_page_name("Index", taken) == "Index-class"
    assert apiscope.unique_page_name("Schema", taken) == "Schema"


def test_module_pages_list_defined_and_reexported_classes(pkg):
    doc = _build(pkg, recursive=True)
    pages = {p.module.__name__: p for p in _iter_pages(doc) if isinstance(p, mk.MkModulePage)}
    root = pages["apidocpkg"]
    assert [k.__name__ for k in root.klasses] == ["Defined", "Hidden", "Orphan"]
    assert [k.__name__ for k in root.reexported] == ["Foo", "Schema"]
    schema = pages["apidocpkg.schema"]
    assert [k.__name__ for k in schema.klasses] == ["Schema", "SchemaHelper"]
    assert not schema.reexported


async def test_links_point_to_class_pages(pkg):
    doc = _build(pkg, recursive=True)
    pages = {p.resolved_file_path: p for p in _iter_pages(doc)}
    schema_cls = sys.modules["apidocpkg.schema"].Schema
    links = doc.ctx.links
    assert links.link_for_klass(schema_cls, from_page=pages["API/index.md"]) == (
        "[Schema](schema/Schema.md)"
    )
    from_foo = pages["API/sub/impl/Foo.md"]
    assert links.link_for_klass(schema_cls, from_page=from_foo) == (
        "[Schema](../../schema/Schema.md)"
    )
    module = sys.modules["apidocpkg.sub"]
    assert links.link_for_module(module, from_page=from_foo) == "[apidocpkg.sub](../index.md)"
    md = await pages["API/index.md"].to_markdown()
    assert "(schema/Schema.md)" in md
    assert "(sub/impl/Foo.md)" in md
    md = await from_foo.to_markdown()  # "Base classes" table
    assert "(../../schema/Schema.md)" in md
    # same folder: keep a folder part, so link replacers leave the link alone
    from_helper = pages["API/schema/SchemaHelper.md"]
    assert links.link_for_klass(schema_cls, from_page=from_helper) == "[Schema](./Schema.md)"
    module = sys.modules["apidocpkg.schema"]
    assert links.link_for_module(module, from_page=from_helper) == (
        "[apidocpkg.schema](./index.md)"
    )


def test_mkdocstrings_use_defining_path(pkg):
    doc = _build(pkg, recursive=True)
    pages = {p.klass.__name__: p for p in _iter_pages(doc) if isinstance(p, mk.MkClassPage)}
    assert pages["Schema"].obj_path == "apidocpkg.schema.Schema"
    assert pages["Hidden"].obj_path == "apidocpkg._impl.Hidden"
    assert pages["Foo"].obj_path == "apidocpkg.sub.impl.Foo"
    # griffe can't resolve `collections.abc` members, fall back to the defining module
    page = mk.MkClassPage(MutableMapping)
    assert page.obj_path == "_collections_abc.MutableMapping"


def test_not_recursive_puts_all_exported_classes_into_root(pkg):
    doc = _build(pkg)
    pages = _class_pages(doc)
    assert pages == {
        "apidocpkg.Defined": "API/Defined.md",
        "apidocpkg._impl.Hidden": "API/Hidden.md",
        "apidocpkg.schema.Schema": "API/Schema.md",
        "apidocpkg.sub.impl.Foo": "API/Foo.md",
    }
    assert not [c for c in doc.get_children() if isinstance(c, mk.MkDoc)]


def test_filter_by_all(pkg):
    doc = _build(pkg, recursive=True, filter_by___all__=True)
    pages = _class_pages(doc)
    # no submodule is listed in the root `__all__`, so all classes live in the root
    assert pages == {
        "apidocpkg.Defined": "API/Defined.md",
        "apidocpkg._impl.Hidden": "API/Hidden.md",
        "apidocpkg.schema.Schema": "API/Schema.md",
        "apidocpkg.sub.impl.Foo": "API/Foo.md",
    }


def test_exclude_modules(pkg):
    doc = _build(pkg, recursive=True)
    doc_excl = mk.MkDoc(pkg, recursive=True, exclude_modules=["sub"], parent=mk.MkNav())
    assert "apidocpkg.sub.impl.Foo" in _class_pages(doc)
    pages = _class_pages(doc_excl)
    assert pages["apidocpkg.sub.impl.Foo"] == "apidocpkg/Foo.md"  # re-exported by root
    assert "apidocpkg.sub._private.SubOrphan" not in pages


if __name__ == "__main__":
    pytest.main([__file__])
