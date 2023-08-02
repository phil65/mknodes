import mknodes

from mknodes.templatenodes import processors


INTRO_TEXT = """Now lets create the documentation.
This code will show how to build a simple documentation section.
"""

SECTION_CODE = "Code for this section"


def create_documentation_section(root_nav: mknodes.MkNav):
    doc_section = root_nav.add_nav("Documentation")

    overview = doc_section.add_index_page(hide_toc=True, icon="material/api")
    overview += mknodes.MkCode.for_object(
        create_documentation_section,
        header=SECTION_CODE,
    )
    overview += mknodes.MkAdmonition(INTRO_TEXT, typ="tip")
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
