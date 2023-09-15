import mknodes as mk

from mknodes import paths
from mknodes.manual import routing
from mknodes.pages import processors
from mknodes.project import Project


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

ANNOTATIONS_INFO = """It is always best to use annotations from the *closest* node.
(We could also have used the annotations from MKPage, but since this source code
is displayed by the MkCode node, we use that one.)"""


nav = mk.MkNav("Navigation & Pages")


def create_navs_section(root_nav: mk.MkNav):
    """Add the complete "The Nodes" section to given MkNav."""
    # Basic structure: Theres one root MkNav, MkNavs can contain MkPages and other MkNavs,
    # MkPages contain more atomic MkNodes, like MkText, MkTable, and MkDiagrams.
    # These markup nodes in some cases can contain other Markup nodes.
    # It`s all one big tree.

    # MkNavs can either be populated manually with MkPages and MkNavs, or we can load
    # existing folders containing markup files. There are two ways for this:
    #
    #   * Load an existing SUMMARY.md and create a nav based on given file content.
    #
    root_nav += nav

    create_from_file_section(nav)

    #   * Load all .md files from a directory tree and create the Navs based on these.
    create_from_folder_section(nav)

    # Another approach to set up navs is by using decorators. We will explain that here:
    routing.create_routing_section(nav)

    # Navs contain also contain pages. This section provides some info how to use MkPages.
    create_mkpage_section(nav)

    create_mkdoc_section(nav)

    # and then we create the index page (the page you are lookin at right now)

    page = nav.add_index_page(hide_toc=True, icon="fontawesome/solid/folder-tree")
    page += mk.MkCommentedCode(create_navs_section, header=SECTION_CODE)
    page += mk.MkDetailsBlock(INTRO_TEXT, expand=True)
    page += mk.MkHeader("All the navs")
    page += mk.MkClassDiagram(mk.MkNav, mode="subclasses", direction="LR", max_depth=3)
    # A nav section corresponds to a `SUMMARY.md`. You can see that when stringifying it.
    text = str(nav)
    text = text.replace("](", "] (")  ##
    page += mk.MkCode(text, header="The resulting MkNav")


def create_from_file_section(nav: mk.MkNav):
    """Load an existing SUMMARY.md and attach it to given MkNav."""
    # We will now demonstate loading an existing Nav tree.

    # This path contains Markdown files/ folders and a pre-populated SUMMARY.md.
    folder = paths.TEST_RESOURCES / "nav_tree/"  # Folder content: # (1)
    summary_file = folder / "SUMMARY.md"  # File content: # (2)

    # We will load it as an MkNav...
    from_file_nav = mk.MkNav.from_file(
        summary_file,
        section="From file",
        hide_toc=True,
        parent=nav,
    )

    # ... and attach that sub-tree to our main tree.
    nav["From file"] = from_file_nav

    # Finally, the page you are seeing right now.
    page = from_file_nav.add_index_page(hide_toc=True, icon="file")
    code = mk.MkCode.for_object(create_from_file_section, header=SECTION_CODE)
    page += code

    text = summary_file.read_text()
    text = text.replace("](", "] (")  ##
    # we are wrapping some annotations with Admonitions, that seems to help
    # with nesting / escaping issues in some cases (and it looks nice!).
    path = paths.TEST_RESOURCES / "nav_tree/"
    tree_node = mk.MkTreeView(path, header="Directory tree")
    code.annotations[1] = mk.MkAdmonition(tree_node)
    file_content_node = mk.MkCode(text, header="SUMMARY.md content")
    code.annotations[2] = mk.MkAdmonition(file_content_node)
    code.annotations[3] = ANNOTATIONS_INFO  # (3)

    # we could also add the annotiation nodes to the page of course:
    page += tree_node
    page += file_content_node


def create_from_folder_section(nav: mk.MkNav):
    """Create a MkNav based on a folder tree containing markup files."""
    # We are using a part of the previous nav tree. It's a subfolder without a SUMMARY.md.
    folder = paths.TEST_RESOURCES / "nav_tree/test_folder/"

    # First, we create the MkNav based on folder content (DocStrings for from_folder: (1))
    from_folder_nav = mk.MkNav.from_folder(folder, parent=nav, hide_toc=True)

    # ... and then attach that sub-tree to our main tree.
    nav["From folder"] = from_folder_nav

    # As you can see in the menu to the left,
    # the menu entries are labelled using the filenames in this case.

    # Finally, create the index page.
    code = mk.MkCode.for_object(create_from_folder_section, header=SECTION_CODE)
    page = from_folder_nav.add_index_page(hide_toc=True, icon="folder")
    page += code
    page += mk.MkTreeView(folder)  # DocStrings: (2)
    folder_docs = mk.MkDocStrings(mk.MkNav.from_folder)
    node_docs = mk.MkDocStrings(mk.MkTreeView)
    code.annotations[1] = folder_docs
    code.annotations[2] = node_docs


def create_mkpage_section(nav: mk.MkNav):
    """Create "MkPage" sub-MkNav and attach it to given MkNav."""
    mkpage_nav = nav.add_nav("MkPage")
    page = mkpage_nav.add_index_page(hide_toc=True)
    page += mk.MkCode.for_object(create_mkpage_section, header=SECTION_CODE)
    page += mk.MkAdmonition(MKPAGE_TIP, typ="tip")
    create_adding_to_mkpages_page(mkpage_nav)
    create_metadata_page(mkpage_nav)
    create_mkclasspage_page(mkpage_nav)
    create_mkmodulepage_page(mkpage_nav)


def create_mkclasspage_page(nav: mk.MkNav):
    page = nav.add_page("MkClassPage", icon=mk.MkClassPage.ICON)
    page += mk.MkCode.for_object(create_mkclasspage_page, header=PAGE_CODE)
    class_page = mk.MkClassPage(mk.MkCode, inclusion_level=False)
    page += mk.MkReprRawRendered(class_page)


def create_mkmodulepage_page(nav: mk.MkNav):
    page = nav.add_page("MkModulePage", icon=mk.MkModulePage.ICON)
    page += mk.MkCode.for_object(create_mkmodulepage_page, header=PAGE_CODE)
    module_page = mk.MkModulePage(mk, inclusion_level=False)
    page += mk.MkReprRawRendered(module_page)


def create_adding_to_mkpages_page(nav: mk.MkNav):
    """Create the "Adding to MkPages" MkPage and attach it to given MkNav."""
    page = nav.add_page(
        "Adding to MkPages",
        hide_toc=True,  # you can set all kinds of metadata for your pages
        hide_path=True,
        icon=mk.MkPage.ICON,
        status="new",
    )
    page += mk.MkCode.for_object(create_adding_to_mkpages_page, header=PAGE_CODE)
    page += mk.MkAdmonition("You can add other MkNodes to a page sequentially.")
    page += "Adding strings also works, they get converted to MkText nodes."
    page += "### ...and text starting with # will become a MkHeader."
    page += "Every MkPage has a MkFootNotes node built-in[^1]."
    page.footnotes[1] = "Super cool, right?"


def create_metadata_page(nav: mk.MkNav):
    """Create the "Metadata" MkPage and attach it to given nav."""
    page = nav.add_page(
        title="Metadata",
        icon="simple/yaml",
        status="deprecated",
        search_boost=2.0,
        subtitle="Subtitle",
        description="Description",
    )
    page += mk.MkCode.for_object(create_metadata_page, header=PAGE_CODE)
    # page.metadata is a dataclass, we can prettyprint these with MkPrettyPrint.
    page += mk.MkPrettyPrint(page.metadata)
    page += mk.MkHtmlBlock(str(page))


def create_mkdefaultwebsite_section(nav: mk.MkNav):
    """Create the "MkDefaultWebsite" sub-MkNav and attach it to given nav."""
    proj = Project.for_path("https://github.com/mkdocstrings/mkdocstrings.git")
    website_nav = mk.MkDefaultWebsite(project=proj)
    nav += website_nav


def create_mkdoc_section(nav: mk.MkNav):
    """Create the "Metadata" sub-MkNav and attach it to given nav."""
    mkdoc_nav = nav.add_nav("MkDoc")

    page = mkdoc_nav.add_index_page(hide_toc=True, icon="api")
    page += mk.MkCode.for_object(create_mkdoc_section, header=SECTION_CODE)
    page += mk.MkAdmonition(DOC_TEXT, typ="tip")
    create_mknodes_section(mkdoc_nav)

    # We could also filter specific subclasses,
    # or do other fancy stuff to generate a customized, automated documentation
    # like changing the default class page ("MkClassPage") of our docs,
    # (The default contains MkDocStrings, a table for base classes,  eventual subclasses
    # and an inheritance graph.)

    # There is also an extension available for this module which offers tools and
    # new nodes based on PySide6 / PyQt6. We can add its documentation easily:
    # from prettyqt import prettyqtmarkdown

    # addon_docs = nav.add_doc(module=prettyqtmarkdown, flatten_nav=True)
    # addon_docs.collect_classes(recursive=True)


def create_mknodes_section(nav: mk.MkNav):
    # lets create the documentation for our module.
    # For that, we can use the MkDoc node, which will generate docs for us.
    # Usually, this can be done with 2 or 3 lines of code, but
    # since our aim is to always show the code which generated the site, we will have to
    # do some extra steps and adjust the default page template.
    # So lets subclass MkClassPage and extend it.
    # First, we write a custom processor which fetches the page-building code from the
    # existing processors, puts them into code blocks and adds them to the page.

    class ShowProcessorCodeProcessor(processors.ContainerProcessor):
        ID = "show_processor_code"

        def __init__(
            self,
            *args,
            processors: list[processors.ContainerProcessor] | None = None,
            **kwargs,
        ):
            super().__init__(*args, **kwargs)
            self.processors = processors or []

        def append_block(self, node: mk.MkContainer):
            code = mk.MkCode.for_object(self.append_block)
            nodes: list[mk.MkAdmonition] = []
            admonition = mk.MkAdmonition(
                code,
                collapsible=True,
                typ="quote",
                title=self.__class__.__name__,
            )
            nodes.append(admonition)
            for processor in self.processors:
                # First, we check if the processor gets applied.
                # If yes, we attach a code block.
                if not processor.check_if_apply(node):
                    continue
                code = mk.MkCode.for_object(processor.append_block)
                name = processor.__class__.__name__
                admonition = mk.MkAdmonition(
                    code,
                    collapsible=True,
                    typ="quote",
                    title=name,
                )
                nodes.append(admonition)
            source = (
                node.resolved_file_path
                if isinstance(node, mk.MkPage)
                else node.__class__.__name__
            )
            node += mk.MkAdmonition(
                nodes,
                typ="quote",
                collapsible=True,
                title=f"Source code for *{source}*",
            )

        def get_header(self, node):
            return "Code for the processors"

    # .. and while we are at it, we will also write another processor to add
    # the required extensions to the page:

    class ExtensionInfoProcessor(processors.ContainerProcessor):
        ID = "extension_info"

        def append_block(self, node: mk.MkContainer):
            extensions = ", ".join(f"`{i}`" for i in self.item.REQUIRED_EXTENSIONS)
            node += mk.MkAdmonition(extensions, title="Required extensions")

        def check_if_apply(self, node: mk.MkContainer):
            # only add this section for MkNodes which have required extensions
            return issubclass(self.item, mk.MkNode) and self.item.REQUIRED_EXTENSIONS

    # Now, we write a custom page template which
    # overrides get_processors and includes our new processors.

    class CustomClassPage(mk.MkClassPage):
        def get_pageprocessors(self):
            processors = super().get_pageprocessors()
            code_processor = ShowProcessorCodeProcessor(self.klass, processors=processors)
            extensions_processor = ExtensionInfoProcessor(self.klass)
            # we will add the code at the top and the Extension infobox at the end.
            return [code_processor, *processors, extensions_processor]

    # Of course it would also be possible to write a processor for the Examples section
    # we did earlier.
    # Since we are just demonstrating all functionality, we will skip that though.

    # last step: a custom module page. Thats basically the index.md for a
    # documentation section. We will also insert the source code there.

    class CustomModulePage(mk.MkModulePage):
        def get_pageprocessors(self):
            procs = super().get_pageprocessors()
            code_block = mk.MkCode.for_object(create_mknodes_section)
            header = "Code for this section"
            fn_processor = processors.StaticBlockProcessor(code_block, header=header)
            proc_processor = ShowProcessorCodeProcessor(
                self.module,
                processors=procs,
            )
            return [fn_processor, proc_processor, *procs]

    # Now that we have our custom ClassPage, we can create the documentation.
    # In our case, we only want to document stuff which is listed in "__all__".
    mknodes_docs = nav.add_doc(
        module=mk,
        filter_by___all__=True,
        class_page=CustomClassPage,
        module_page=CustomModulePage,
    )

    # now we collect the stuff we want to document.
    mknodes_docs.collect_classes(recursive=True)

    # We are done. Creating the files will be done when the tree is written in the end.
