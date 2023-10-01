import mknodes as mk


nav = mk.MkNav("Get started")


def create_get_started_section(root_nav: mk.MkNav):
    root_nav += nav
    page = nav.add_index_page()
    page += "Welcome to MkNodes!"


@nav.route.page("Welcome to MkNodes")
def _(page: mk.MkPage):
    page += mk.MkCode.for_file(__file__)


@nav.route.page("Why should I use MkNodes?")
def _(page: mk.MkPage):
    page += mk.MkJinjaTemplate("why_should_i_use_mknodes.jinja")
