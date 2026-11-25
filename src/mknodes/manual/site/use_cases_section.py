import mknodes as mk
from mknodes.site import paths


nav = mk.MkNav("Use cases")


@nav.route.page(is_index=True, hide="toc")
def _(page: mk.MkPage):
    page += mk.MkTemplate("site/use_cases_index.jinja")


@nav.route.page("Creating a website via config", hide="toc")
def _(page: mk.MkPage):
    """Create the "Creating a website via config" MkPage."""
    config = (paths.RESOURCES / "pages_example.toml").read_text("utf-8")
    variables = {"config": config}
    page += mk.MkTemplate("site/use_case_default_website.jinja", variables=variables)
