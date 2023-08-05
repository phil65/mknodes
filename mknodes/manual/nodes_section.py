import mknodes

from mknodes.manual import routing
from mknodes.pages import processors
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

HACK_TEXT = """The replace() is a small hack to prevent links from getting processed
by plugins. Ignore it."""

ANNOTATIONS_INFO = """It is always best to use annotations from the *closest* node.
(We could also have used the annotations from MKPage, but since this source code
is displayed by the MkCode node, we use that one.)"""


def create_nodes_section(root_nav: mknodes.MkNav):
    """Add the complete "The Nodes" section to given MkNav."""
    # Basic structure: Theres one root MkNav, MkNavs can contain MkPages and other MkNavs,
    # MkPages contain more atomic MkNodes, like MkText, MkTable, and MkDiagrams.
    # These markup nodes in some cases can contain other Markup nodes.
    # It`s all one big tree.

    the_nodes_nav = root_nav.add_nav("The nodes")
    # first we create the menu on the left:

    create_mknav_section(the_nodes_nav)
    create_mkpage_section(the_nodes_nav)
    create_base_nodes_section(the_nodes_nav)
    create_template_nodes_section(the_nodes_nav)
    create_mkdoc_section(the_nodes_nav)

    # and then we create the index page (the page you are lookin at right now)

    page = the_nodes_nav.add_index_page(hide_toc=True, icon="material/graph")
    page += mknodes.MkCode.for_object(create_nodes_section, header=SECTION_CODE)
    page += mknodes.MkDetailsBlock(INTRO_TEXT, expand=True)
    page += mknodes.MkHeader("All the nodes")
    page += mknodes.MkClassDiagram(
        mknodes.MkNode,
        mode="subclass_tree",
        orientation="LR",
        max_depth=3,
    )


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


def create_mknav_section(nav: mknodes.MkNav):
    """Add the sub-MkNav "MkNav" to given MkNav."""
    nav_section = nav.add_nav("MkNav")

    # MkNavs can either be populated manually with MkPages and MkNavs, or we can load
    # existing folders containing markup files. There are two ways for this:

    # 1) Load an existing SUMMARY.md and create a nav based on given file content.
    create_from_file_section(nav_section)

    # 2) Load all .md files from a directory tree and create the Navs based on these.
    create_from_folder_section(nav_section)

    # Another approach to set up navs is by using decorators. We will explain that here:
    routing.create_routing_section(nav_section)

    # Every MkNav can have an index page (which corresponds to your index.md)
    # Index pages get inserted first into the menu, so that the mkdocs-section-index
    # plugin can be utizilized.
    page = nav_section.add_index_page(icon=nav.ICON, hide_toc=True)
    code = mknodes.MkCode.for_object(create_mknav_section, header=SECTION_CODE)
    page += code
    # A nav section corresponds to a SUMMARY.md. You can see that when stringifying it.
    text = str(nav_section).replace("](", "] (")  # (1)
    code.annotations[1] = HACK_TEXT
    page += mknodes.MkCode(text, header="The resulting MkNav")


def create_from_file_section(nav: mknodes.MkNav):
    """Load an existing SUMMARY.md and attach it to given MkNav."""
    # We will now demonstate loading an existing Nav tree.

    # This path contains Markdown files/ folders and a pre-populated SUMMARY.md.
    folder = mknodes.TEST_RESOURCES / "nav_tree/"  # Folder content: # (1)
    summary_file = folder / "SUMMARY.md"  # File content: # (2)

    # We will load it as an MkNav...
    from_file_nav = mknodes.MkNav.from_file(
        summary_file,
        section="From file",
        hide_toc=True,
        parent=nav,
    )

    # ... and attach that sub-tree to our main tree.
    nav["From file"] = from_file_nav

    # Finally, the page you are seeing right now.
    page = from_file_nav.add_index_page(hide_toc=True, icon="material/file")
    code = mknodes.MkCode.for_object(create_from_file_section, header=SECTION_CODE)
    page += code

    text = summary_file.read_text().replace("](", "] (")  # (3)
    # we are wrapping some annotations with Admonitions, that seems to help
    # with nesting / escaping issues in some cases (and it looks nice!).
    tree_node = mknodes.MkDirectoryTree(mknodes.TEST_RESOURCES / "nav_tree/")
    code.annotations[1] = mknodes.MkAdmonition(tree_node)
    file_content_node = mknodes.MkCode(text)
    code.annotations[2] = mknodes.MkAdmonition(file_content_node)
    code.annotations[3] = HACK_TEXT
    code.annotations[4] = ANNOTATIONS_INFO  # (4)

    # we could also add the annotiation nodes to the page of course:
    page += tree_node
    page += file_content_node


def create_from_folder_section(nav: mknodes.MkNav):
    """Create a MkNav based on a folder tree containing markup files."""
    # We are using a part of the previous nav tree. It's a subfolder without a SUMMARY.md.
    folder = mknodes.TEST_RESOURCES / "nav_tree/test_folder/"

    # First, we create the MkNav based on folder content (DocStrings for from_folder: (1))
    from_folder_nav = mknodes.MkNav.from_folder(folder, parent=nav, hide_toc=True)

    # ... and then attach that sub-tree to our main tree.
    nav["From folder"] = from_folder_nav

    # As you can see in the menu to the left,
    # the menu entries are labelled using the filenames in this case.

    # Finally, create the index page.
    code = mknodes.MkCode.for_object(create_from_folder_section, header=SECTION_CODE)
    page = from_folder_nav.add_index_page(hide_toc=True, icon="material/folder")
    page += code
    page += mknodes.MkDirectoryTree(folder)  # DocStrings: (2)
    folder_docs = mknodes.MkDocStrings(mknodes.MkNav.from_folder, section_style="list")
    node_docs = mknodes.MkDocStrings(mknodes.MkDirectoryTree, section_style="list")
    code.annotations[1] = folder_docs
    code.annotations[2] = node_docs


def create_mkpage_section(nav: mknodes.MkNav):
    """Create "MkPage" sub-MkNav and attach it to given MkNav."""
    mkpage_nav = nav.add_nav("MkPage")
    page = mkpage_nav.add_index_page(hide_toc=True, icon=mknodes.MkPage.ICON)
    page += mknodes.MkCode.for_object(create_mkpage_section, header=SECTION_CODE)
    page += mknodes.MkAdmonition(MKPAGE_TIP, typ="tip")
    create_adding_to_mkpages_page(mkpage_nav)
    create_metadata_page(mkpage_nav)
    create_mkclasspage_page(mkpage_nav)
    create_mkmodulepage_page(mkpage_nav)


def create_mkclasspage_page(nav: mknodes.MkNav):
    page = nav.add_page("MkClassPage", icon=mknodes.MkClassPage.ICON)
    page += mknodes.MkCode.for_object(create_mkclasspage_page, header=PAGE_CODE)
    class_page = mknodes.MkClassPage(mknodes.MkCode)
    page += mknodes.MkReprRawRendered(class_page)


def create_mkmodulepage_page(nav: mknodes.MkNav):
    page = nav.add_page("MkModulePage", icon=mknodes.MkModulePage.ICON)
    page += mknodes.MkCode.for_object(create_mkmodulepage_page, header=PAGE_CODE)
    module_page = mknodes.MkModulePage(mknodes)
    page += mknodes.MkReprRawRendered(module_page)


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
    page += mknodes.MkText("You can add other MkNodes to a page sequentially.")
    page += "Adding strings also works, they get converted to MkText nodes."
    page += "...and text starting with # will become a MkHeader."
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
    mkdoc_nav = nav.add_nav("MkDoc")

    page = mkdoc_nav.add_index_page(hide_toc=True, icon="material/api")
    page += mknodes.MkCode.for_object(
        create_mkdoc_section,
        header=SECTION_CODE,
    )
    page += mknodes.MkAdmonition(DOC_TEXT, typ="tip")
    create_mknodes_section(mkdoc_nav)

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

    class ShowProcessorCodeProcessor(processors.PageProcessor):
        ID = "show_processor_code"

        def __init__(
            self,
            *args,
            processors: list[processors.PageProcessor] | None = None,
            **kwargs,
        ):
            super().__init__(*args, **kwargs)
            self.processors = processors or []

        def append_block(self, page: mknodes.MkPage):
            code = mknodes.MkCode.for_object(self.append_block)
            page += mknodes.MkAdmonition(
                code,
                collapsible=True,
                title=self.__class__.__name__,
            )
            for processor in self.processors:
                # First, we check if the processor gets applied.
                # If yes, we attach a code block.
                if processor.check_if_apply(page):
                    code = mknodes.MkCode.for_object(processor.append_block)
                    page += mknodes.MkAdmonition(
                        code,
                        collapsible=True,
                        title=processor.__class__.__name__,
                    )

        def get_header(self, page):
            return "Code for the processors"

    # .. and while we are at it, we will also write another processor to add
    # the required extensions to the page:

    class ExtensionInfoProcessor(processors.PageProcessor):
        ID = "extension_info"

        def append_block(self, page: mknodes.MkPage):
            extensions = ", ".join(f"`{i}`" for i in self.item.REQUIRED_EXTENSIONS)
            page += mknodes.MkAdmonition(extensions, title="Required extensions")

        def check_if_apply(self, page: mknodes.MkPage):
            # only add this section for MkNodes which have required extensions
            return issubclass(self.item, mknodes.MkNode) and self.item.REQUIRED_EXTENSIONS

    # Now, we write a custom page template which
    # overrides get_processors and includes our new processors.

    class CustomClassPage(mknodes.MkClassPage):
        def get_processors(self):
            processors = super().get_processors()
            code_processor = ShowProcessorCodeProcessor(self.klass, processors=processors)
            extensions_processor = ExtensionInfoProcessor(self.klass)
            # we will add the code at the top and the Extension infobox at the end.
            return [code_processor, *processors, extensions_processor]

    # Of course it would also be possible to write a processor for the Examples section
    # we did earlier.
    # Since we are just demonstrating all functionality, we will skip that though.

    # last step: a custom module page. Thats basically the index.md for a
    # documentation section. We will also insert the source code there.

    class CustomModulePage(mknodes.MkModulePage):
        def get_processors(self):
            procs = super().get_processors()
            code_block = mknodes.MkCode.for_object(create_mknodes_section)
            fn_processor = processors.StaticBlockProcessor(
                code_block,
                header="Code for this section",
            )
            proc_processor = ShowProcessorCodeProcessor(
                self.module,
                processors=procs,
            )
            return [fn_processor, proc_processor, *procs]

    # Now that we have our custom ClassPage, we can create the documentation.
    # In our case, we only want to document stuff which is listed in "__all__".
    mknodes_docs = nav.add_doc(
        module=mknodes,
        filter_by___all__=True,
        class_page=CustomClassPage,
        module_page=CustomModulePage,
    )

    # now we collect the stuff we want to document.
    mknodes_docs.collect_classes(recursive=True)

    # We are done. Creating the files will be done when the tree is written in the end.
