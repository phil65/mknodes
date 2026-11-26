"""Page templates: wiring templates to pages and moving page resources into them."""

import pathlib
import pprint

import mknodes as mk
from mknodes.utils import log, resources


logger = log.get_logger(__name__)


def create_page_info(page: mk.MkPage, req: resources.Resources) -> mk.MkAdmonition:
    """Create a collapsed admonition box showing some page-related data.

    Args:
        page: Page to create the info box for.
        req: Resources of the page (passed in to avoid having to collect them again)
    """
    adm = mk.MkAdmonition([], title="Page info", typ="theme", collapsible=True, parent=page)

    if page.created_by:
        typ = "section" if page.is_index() else "page"
        code = mk.MkCode.for_object(page.created_by)
        title = f"Code for this {typ}"
        details = mk.MkAdmonition(code, title=title, collapsible=True, typ="quote")
        adm += details

    pretty = mk.MkCode(pprint.pformat(req))
    details = mk.MkAdmonition(pretty, title="Resources", collapsible=True, typ="quote")
    adm += details

    code = mk.MkCode(str(page.resolved_metadata), language="yaml")
    details = mk.MkAdmonition(code, title="Metadata", collapsible=True, typ="quote")
    adm += details
    return adm


def update_page_template(page: mk.MkPage):
    """Set template filename, metadata reference and `extends` path for given page.

    Args:
        page: Page of the template
    """
    if page.template:
        node_path = pathlib.Path(page.resolved_file_path)
    elif any(i.page_template for i in page.parent_navs):
        nav = next(i for i in page.parent_navs if i.page_template)
        node_path = pathlib.Path(nav.resolved_file_path)
    else:
        node_path = None
    if node_path:
        html_path = node_path.with_suffix(".html").as_posix()
        logger.debug("Updated template for MkPage %r: %r", page.title, html_path)
        page.metadata.template = html_path
        if page.template:
            page.template.filename = html_path
            if extends := _get_extends_from_parent(page):
                page.template.extends = extends


def update_nav_template(nav: mk.MkNav):
    """Set template filename, metadata reference and `extends` path for given nav.

    Args:
        nav: Nav of the template
    """
    if nav.page_template:
        path = pathlib.Path(nav.resolved_file_path)
        html_path = path.with_suffix(".html").as_posix()
        logger.debug("Updated template for MkNav %r: %r", nav.title, html_path)
        nav.metadata.template = html_path
        nav.page_template.filename = html_path
        if extends := _get_extends_from_parent(nav):
            nav.page_template.extends = extends


async def move_resources_to_template(
    page: mk.MkPage, req: resources.Resources | None = None
) -> resources.Resources:
    """Add resources from page to its template and return the "filtered" resources.

    Args:
        page: Page to process resources for
        req: Pre-computed resources. If None, will call page.get_resources()
    """
    if req is None:
        req = await page.get_resources()
    js_reqs: list[resources.JSFile] = []
    prefix = "../" * (len(page.resolved_parts) + 1)
    for i in req.js:
        if isinstance(i, resources.JSText):
            js_file = resources.JSFile(
                link=f"{prefix}assets/{i.resolved_filename}",
                async_=i.async_,
                defer=i.defer,
                crossorigin=i.crossorigin,
                typ=i.typ,
                is_library=i.is_library,
            )
        else:
            js_file = i
        js_reqs.append(js_file)
    non_libs = [i for i in js_reqs if not i.is_library]
    libs = [i for i in js_reqs if i.is_library]
    assets = [i.get_asset() for i in req.js if isinstance(i, resources.JSText)]
    req.assets += assets
    req.js = []
    for lib in libs:
        msg = f"Adding {lib.link!r} lib to {page.resolved_file_path!r} template"
        logger.info(msg)
        if page.template is not None:  # (an empty template is falsy)
            page.template.libs.add_script_file(lib)
    for lib in non_libs:
        msg = f"Adding {lib.link!r} script to {page.resolved_file_path!r} template"
        logger.info(msg)
        if page.template is not None:  # (an empty template is falsy)
            page.template.scripts.add_script_file(lib)
    css_reqs: list[resources.CSSFile] = []
    for css_item in req.css:
        if isinstance(css_item, resources.CSSText):
            css_file = resources.CSSFile(link=f"{prefix}assets/{css_item.resolved_filename}")
        else:
            css_file = css_item
        css_reqs.append(css_file)
    assets = [i.get_asset() for i in req.css if isinstance(i, resources.CSSText)]
    req.assets += assets
    req.css = []
    for css_ in css_reqs:
        msg = f"Adding {css_.link!r} stylesheet to {page.resolved_file_path!r} template"
        logger.info(msg)
        if page.template is not None:  # (an empty template is falsy)
            page.template.styles.add_stylesheet(css_)
    return req


def _get_extends_from_parent(node: mk.MkPage | mk.MkNav) -> str | None:
    """Check parent navs for a page template and return its path if one was found.

    Args:
        node: Node to get the `extends` path for
    """
    for nav in node.parent_navs:
        if nav.page_template:
            p = pathlib.Path(nav.resolved_file_path)
            return p.with_suffix(".html").as_posix()
    return None
