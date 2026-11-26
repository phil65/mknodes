"""Manual section for the site generator (`mknodes build` / `serve` / `generate`)."""

import mknodes as mk
from mknodes.manual.site import cli_section, use_cases_section
from mknodes.site import paths


nav = mk.MkNav("Site generator")

INTRO = (
    "This section provides an overview about the sequence of operations applied by"
    " **MkNodes** when running the full build process."
)


@nav.route.page(is_index=True, hide="toc")
def _(page: mk.MkPage):
    page += mk.MkTemplate("site/index.jinja")


@nav.route.page("Configuration", hide="toc")
def _(page: mk.MkPage):
    page += mk.MkTemplate("site/configuration.jinja")
    page += mk.MkDocStrings(
        "mknodes.site.settings.GeneratorSettings",
        show_root_toc_entry=False,
        show_if_no_docstring=True,
        heading_level=4,
        show_bases=False,
        show_source=False,
    )


@nav.route.page("Site engines", hide="toc")
def _(page: mk.MkPage):
    page += mk.MkTemplate("site/engines.jinja")


@nav.route.page("The build process", hide="toc")
def _(page: mk.MkPage):
    page += INTRO
    page += mk.MkTimeline(paths.RESOURCES / "timeline_data.toml")


nav += use_cases_section.nav
nav += cli_section.nav
