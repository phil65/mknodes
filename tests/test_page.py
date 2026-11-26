import pytest

import mknodes as mk


def test_page():
    page = mk.MkPage()
    page.metadata.pop("created")
    assert not str(page)


def test_next_and_previous_page():
    nav = mk.MkNav()
    page_1 = nav.add_page("Page 1")
    page_2 = nav.add_page("Page 2")
    assert page_1.previous_page is None
    assert page_1.next_page is page_2
    assert page_2.previous_page is page_1
    assert page_2.next_page is None


def test_next_and_previous_page_across_navs():
    nav = mk.MkNav()
    sub_1 = nav.add_nav("Sub 1")
    sub_2 = nav.add_nav("Sub 2")
    page_1 = sub_1.add_page("Page 1")
    page_2 = sub_2.add_page("Page 2")
    assert page_1.previous_page is None
    assert page_1.next_page is page_2
    assert page_2.previous_page is page_1
    assert page_2.next_page is None
    page_3 = nav.add_page("Page 3")
    assert page_2.next_page is page_3
    assert page_3.previous_page is page_2


EXPECTED = """---
description: Some description
hide:
- toc
- path
icon: material/emoticon-happy
search:
  boost: 2.0
  exclude: false
status: new
subtitle: Some subtitle
title: Some title
---
"""


def test_metadata():
    page = mk.MkPage(
        hide="toc,path",
        search_boost=2.0,
        exclude_from_search=False,
        icon="material/emoticon-happy",
        status="new",
        title="Some title",
        subtitle="Some subtitle",
        description="Some description",
    )
    page.metadata.pop("created")
    assert page.metadata.as_page_header() == EXPECTED


@pytest.mark.parametrize(
    "node",
    [
        mk.MkList(["a", "b"]),
        mk.MkTable({"A": ["1", "2"], "B": ["3", "4"]}),
        mk.MkDefinitionList({"key": "value"}),
    ],
    ids=lambda x: type(x).__name__,
)
async def test_nested_node_keeps_its_own_markdown(node: mk.MkNode):
    """Containers must not discard markdown of subclasses overriding to_md_unprocessed."""
    expected = await node.to_md_unprocessed()
    page = mk.MkPage()
    page += node
    assert expected.strip() in await page.to_markdown()


if __name__ == "__main__":
    pytest.main([__file__])


def _create_page() -> mk.MkPage:
    return mk.MkPage("Created")


def test_created_metadata_points_to_user_code():
    import asyncio
    import threading

    from anyenv import run_sync

    async def create_async() -> mk.MkPage:
        return _create_page()

    pages = [_create_page(), run_sync(create_async()), asyncio.run(create_async())]
    thread = threading.Thread(target=lambda: pages.append(_create_page()))
    thread.start()
    thread.join()
    nav = mk.MkNav()
    pages.append(nav.add_page("Added"))
    for page in pages:
        created = page.metadata["created"]
        assert created["source_filename"] == __file__
        expected = {"_create_page", "test_created_metadata_points_to_user_code"}
        assert created["source_function"] in expected


def test_created_metadata_of_routed_page():
    nav = mk.MkNav()

    @nav.route.page("Routed")
    def routed(page: mk.MkPage):
        page += "text"

    page = nav.nav["Routed"]
    assert page.created_by is routed
    created = page.metadata["created"]
    assert created["source_filename"] == __file__
    assert created["source_function"].endswith("routed")
