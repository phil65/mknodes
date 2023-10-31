import mknodes as mk


nav = mk.MkNav("MkPages")


@nav.route.page(is_index=True)
def _(page: mk.MkPage):
    page += mk.MkTemplate("pages/mkpage_index.jinja")
    page.footnotes[1] = r"Footnotes are numbered, can be set via \__setitem__."
    page.footnotes[2] = r"They can also get nested[^3]."
    page.footnotes[3] = mk.MkAdmonition("They can also contain other Markdown (nodes).")


@nav.route.page("MkClassPage")
def _(page: mk.MkPage):
    variables = dict(example_class=mk.MkCode)
    page += mk.MkTemplate("pages/mkclasspage.jinja", variables=variables)


@nav.route.page("MkModulePage")
def _(page: mk.MkPage):
    import mkdocs.config

    variables = dict(example_module=mkdocs.config)
    page += mk.MkTemplate("pages/mkmodulepage.jinja", variables=variables)


@nav.route.page("Setting the homepage")
def _(page: mk.MkPage):
    page += mk.MkTemplate("pages/homepage.jinja")


@nav.route.page("Adding to MkPages", hide="toc", status="new")
def _(page: mk.MkPage):
    page += mk.MkAdmonition("You can add other MkNodes to a page sequentially.")
    page += "Adding strings also works, they get converted to MkText nodes."
    page += "### ...and text starting with # will become a MkHeader."
    page += "Every MkPage has a MkFootNotes node built-in[^1]."
    page.footnotes[1] = "Super cool, right?"


@nav.route.page(
    "Metadata",
    status="deprecated",
    search_boost=2.0,
    subtitle="Subtitle",
    description="Description",
)
def _(page: mk.MkPage):
    page += mk.MkTemplate("pages/page_metadata.jinja")


@nav.route.page("Templates", hide="toc", status="new")
def _(page: mk.MkPage):
    page += mk.MkTemplate("pages/page_templates.jinja")
    page.template.announce.content = mk.MkMetadataBadges(typ="classifiers")
    page.template.footer.content = mk.MkProgressBar(50)
    code = "information = 'You can even put MkNodes here!'"
    page.template.tabs.content = mk.MkCode(f"{code}")
    page.template.hero.content = mk.MkHeader("A header!")
    css = {
        ":root": {
            "--md-primary-fg-color": "#FF0000",
            "--md-primary-fg-color--light": "#FF0000",
            "--md-primary-fg-color--dark": "#FF0000",
        },
    }
    page.template.styles.add_css(css)


@nav.route.page("Resources")
def _(page: mk.MkPage):
    page += mk.MkTemplate("resources.jinja")
