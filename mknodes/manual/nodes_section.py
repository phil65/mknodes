import mknodes

from mknodes.templatenodes import processors
from mknodes.utils import classhelpers


DOC_TEXT = """Now lets create the documentation.
This code will show how to build a simple documentation section.
"""


INTRO_TEXT = """
Basically everything interesting in this library inherits from MkNode.
It`s the base class for all tree nodes we are building. The tree goes from the root nav
down to single markup elements. We can show the subclass tree by using
the MkClassDiagram Node.
"""

MKPAGE_TIP = "MkPages can also be loaded from files by using MkPage.from_file"

SECTION_CODE = "Code for this section"
PAGE_CODE = "Code for this page"


def create_nodes_section(root_nav: mknodes.MkNav):
    """Add the complete "The Nodes" section to given MkNav."""
    # Basic structure: Theres one root MkNav, MkNavs can contain MkPages and other MkNavs,
    # MkPages contain more atomic MkNodes, like MkText, MkTable, and MkDiagrams.
    # These markup nodes in some cases can contain other Markup nodes.
    # It`s all one big tree.

    the_nodes_nav = root_nav.add_nav("The nodes")
    overview = the_nodes_nav.add_index_page(hide_toc=True, icon="material/graph")

    # this here is what you are reading right now.
    overview += mknodes.MkCode.for_object(create_nodes_section, header=SECTION_CODE)
    overview += mknodes.MkDetailsBlock(INTRO_TEXT, expand=True)
    # let`s take a look at some of the mentioned Markup nodes.
    # we will now iter all node classes, create a small page (which is part of the menu)
    # and put that page as a link into a table, combined with docstrings.
    create_mknav_section(the_nodes_nav)
    create_mkpage_section(the_nodes_nav)
    create_base_nodes_section(the_nodes_nav)
    create_template_nodes_section(the_nodes_nav)
    create_mkdoc_section(the_nodes_nav)
    create_subclass_page(the_nodes_nav)


def create_base_nodes_section(nav: mknodes.MkNav):
    """Add a sub-MkNav containing all base node pages to given MkNav."""
    all_classes = list(classhelpers.iter_subclasses(mknodes.MkNode))
    klasses = [kls for kls in all_classes if ".basenodes." in kls.__module__]
    base_nodes_nav = nav.add_nav("Base nodes")
    page = base_nodes_nav.add_index_page(hide_toc=True, icon="material/puzzle-outline")
    page += mknodes.MkCode.for_object(create_base_nodes_section, header=SECTION_CODE)
    page += mknodes.MkCode.for_object(create_section_for_nodes)
    page += create_section_for_nodes(base_nodes_nav, klasses)


def create_template_nodes_section(nav: mknodes.MkNav):
    """Add a sub-MkNav containing all template node pages to given MkNav."""
    all_classes = list(classhelpers.iter_subclasses(mknodes.MkNode))
    klasses = [kls for kls in all_classes if ".templatenodes." in kls.__module__]
    template_nodes_nav = nav.add_nav("Template nodes")
    icon = "fontawesome/solid/puzzle-piece"
    page = template_nodes_nav.add_index_page(hide_toc=True, icon=icon)
    page += mknodes.MkCode.for_object(create_template_nodes_section, header=SECTION_CODE)
    page += mknodes.MkCode.for_object(create_section_for_nodes)
    page += create_section_for_nodes(template_nodes_nav, klasses)


def create_section_for_nodes(nav: mknodes.MkNav, klasses: list[type]) -> mknodes.MkTable:
    """Add a MkPage to the MkNav for each class, create a index MkTable and return it."""
    table = mknodes.MkTable(columns=["Node", "Docstrings", "Markdown extensions"])
    for kls in klasses:
        # iter_subclasses just calls __subclasses__ recursively.
        if "create_example_page" in kls.__dict__:
            # All MkNode classes carry some metadata, like ICON or REQUIRED_EXTENSIONS.
            # We can use that for building the docs.
            page = nav.add_page(kls.__name__, icon=kls.ICON)
            create_class_page(kls, page)
            link = mknodes.MkLink(page, kls.__name__, icon=kls.ICON)
            extensions = ", ".join(f"`{i}`" for i in kls.REQUIRED_EXTENSIONS)
            table.add_row((link, kls.__doc__, extensions))
    return table


def create_class_page(kls: type, page: mknodes.MkPage):
    """Create a MkPage with example code for given klass."""
    # Each example page will begin by displaying the code used to create the page.
    page += mknodes.MkCode.for_object(
        create_class_page,
        extract_body=True,
        header=PAGE_CODE,
    )
    page += mknodes.MkCode.for_object(kls.create_example_page, extract_body=True)
    # and afterwards, we show what was added to the page.
    page += "## Output"
    kls.create_example_page(page)


def create_subclass_page(nav: mknodes.MkNav):
    """Add a MkPage containing a inheritance tree diagram to given MkNav."""
    # Lets take a look at the relations of the included nodes.
    # It`s easy to show different diagrams for classes.
    subcls_page = nav.add_page(
        "Inheritance tree",
        hide_toc=True,
        icon="octicons/git-merge-16",
    )
    subcls_page += mknodes.MkCode.for_object(create_subclass_page, header=PAGE_CODE)
    subcls_page += mknodes.MkClassDiagram(
        mknodes.MkNode,
        mode="subclass_tree",
        orientation="LR",
    )


def create_mknav_section(nav: mknodes.MkNav):
    """Add the sub-MkNav "MkNav" to given MkNav."""
    nav_section = nav.add_nav("MkNav")
    # MkNavs can either be populated manually with MkPages and MkNavs, or we can load
    # existing folders containing markup files. There are two ways for this:
    # 1) Load an existing SUMMARY.md and create a nav based on given file content.
    create_from_file_section(nav_section)
    # 2) Load all .md files from a directory tree and create the Navs based on these.
    create_from_folder_section(nav_section)
    # Every MkNav can have an index page (which corresponds to your index.md))
    # Index pages get inserted first into the menu, so that the mkdocs-section-index
    # plugin can be utizilized.
    nav_page = nav_section.add_index_page(icon=nav.ICON, hide_toc=True)
    nav_page += mknodes.MkCode.for_object(create_mknav_section, header=SECTION_CODE)
    # A nav section corresponds to a SUMMARY.md. You can see that when stringifying it.
    nav_page += mknodes.MkCode(
        str(nav_section).replace("](", "] ("),
        header="File content",
    )


def create_from_file_section(nav: mknodes.MkNav):
    """Load an existing SUMMARY.md and attach it to given MkNav."""
    file = mknodes.TEST_RESOURCES / "nav_tree/SUMMARY.md"
    file_nav = mknodes.MkNav.from_file(file, section="From file", parent=nav)
    nav["From file"] = file_nav
    page = file_nav.add_index_page(hide_toc=True, icon="material/file")
    page += mknodes.MkCode.for_object(create_from_file_section, header=SECTION_CODE)
    page += "Content of SUMMARY.md"
    page += mknodes.MkCode(file.read_text().replace("](", "] ("))  # quick hack to prevent
    # link replacer plugin from modifying the code


def create_from_folder_section(nav: mknodes.MkNav):
    # We are using a part of the previous nav tree. It's a subfolder without a SUMMARY.md.
    folder = mknodes.TEST_RESOURCES / "nav_tree/test_folder/"
    folder_nav = mknodes.MkNav.from_folder(folder, parent=nav)
    nav["From folder"] = folder_nav
    # As you can see in the menu, the menu entries are labelled using the filenames
    # in this case.
    page = folder_nav.add_index_page(hide_toc=True, icon="material/folder")
    page += mknodes.MkCode.for_object(create_from_folder_section, header=SECTION_CODE)


def create_mkpage_section(nav: mknodes.MkNav):
    """Create "MkPage" sub-MkNav and attach it to given MkNav."""
    page_section = nav.add_nav("MkPage")
    overview = page_section.add_index_page(hide_toc=True, icon=mknodes.MkPage.ICON)
    overview += mknodes.MkCode.for_object(
        create_mkpage_section,
        header=SECTION_CODE,
    )
    overview += mknodes.MkAdmonition(MKPAGE_TIP, typ="tip")
    create_adding_to_mkpages_page(page_section)
    create_metadata_page(page_section)


def create_adding_to_mkpages_page(nav: mknodes.MkNav):
    """Create the "Adding to MkPages" MkPage and attach it to given MkNav."""
    page = nav.add_page(
        "Adding to MkPages",
        hide_toc=True,  # you can set all kinds of metadata for your pages
        hide_path=True,
        icon=mknodes.MkPage.ICON,
        status="new",
    )
    page += mknodes.MkCode.for_object(create_adding_to_mkpages_page, header=PAGE_CODE)
    page += mknodes.MkAdmonition("You can add other MkNodes to a page sequentially.")
    page.add_header("MkPage also has some add_xyz methods", level=2)
    page += "Adding strings also works, they get converted to MkText nodes."
    page += "Every MkPage has a MkFootNotes node built-in[^1]."
    page.footnotes[1] = "Super cool, right?"


def create_metadata_page(nav: mknodes.MkNav):
    """Create the "Metadata" MkPage and attach it to given nav."""
    page = nav.add_page(
        "Metadata",
        icon="simple/yaml",
        status="deprecated",
        search_boost=2.0,
        title="Some title",
        subtitle="Subtitle",
        description="Description",
    )
    metadata = str(page)
    page += mknodes.MkCode.for_object(create_metadata_page, header=PAGE_CODE)
    page += mknodes.MkCode(metadata, language="yaml")
    page += mknodes.MkHtmlBlock(str(page))


def create_mkdoc_section(nav: mknodes.MkNav):
    """Create the "Metadata" sub-MkNav and attach it to given nav."""
    doc_section = nav.add_nav("MkDoc")

    overview = doc_section.add_index_page(hide_toc=True, icon="material/api")
    overview += mknodes.MkCode.for_object(
        create_mkdoc_section,
        header=SECTION_CODE,
    )
    overview += mknodes.MkAdmonition(DOC_TEXT, typ="tip")
    create_mknodes_section(doc_section)

    # We could also filter specific subclasses,
    # or do other fancy stuff to generate a customized, automated documentation
    # like changing the default class page ("MkClassPage") of our docs,
    # (The default contains MkDocStrings, a table for base classes,  eventual subclasses
    # and an inheritance graph.)

    # There is also an extension available for this module which offers tools and
    # new nodes based on PySide6 / PyQt6. We can add its documentation easily:
    # from prettyqt import prettyqtmarkdown

    # addon_docs = doc_section.add_doc(module=prettyqtmarkdown, flatten_nav=True)
    # addon_docs.collect_classes(recursive=True)


def create_mknodes_section(nav: mknodes.MkNav):
    # lets create the documentation for our module.
    # For that, we can use the MkDoc node, which will generate docs for us.
    # Usually, this can be done with 2 or 3 lines of code, but
    # since our aim is to always show the code which generated the site, we will have to
    # do some extra steps and adjust the default page template.
    # So lets subclass MkClassPage and extend it.
    # First, we write a custom processor which fetches the page-building code from the
    # existing processors, puts them into code blocks and adds them to the page.

    class SourceCodeProcessor(processors.PageProcessor):
        def __init__(
            self,
            *args,
            processors: list[processors.PageProcessor] | None = None,
            **kwargs,
        ):
            super().__init__(*args, **kwargs)
            self.processors = processors or []

        def append_block(self, page: mknodes.MkPage):
            for processor in self.processors:
                # First, we check if the processor gets applied.
                # If yes, we attach a code block.
                if processor.check_if_apply(page):
                    page += mknodes.MkCode.for_object(processor.append_block)

        def get_header(self, page):
            return "Code for this page"

    # Now, we write a custom page template which
    # overrides get_processors and includes our new processor at the beginning.

    class CustomClassPage(mknodes.MkClassPage):
        def get_processors(self):
            processors = super().get_processors()
            code_processor = SourceCodeProcessor(self.klass, processors=processors)
            return [code_processor, *processors]

    # Now that we have our custom ClassPage, we can create the documentation.
    # In our case, we only want to document stuff which is listed in "__all__".
    mknodes_docs = nav.add_doc(
        module=mknodes,
        filter_by___all__=True,
        class_page=CustomClassPage,
    )

    # now we collect the stuff we want to document.
    mknodes_docs.collect_classes(recursive=True)
