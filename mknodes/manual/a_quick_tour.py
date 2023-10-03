import mknodes as mk


def a_quick_tour(page: mk.MkPage):
    # This will be a quick, short random introduction of some of the nodes
    # included in **MkNodes**.
    # The selection of nodes is totally random, this should just provide a quick overview
    # how to interact with the nodes.
    #
    # Let the tour begin!
    #
    # Our first [MkNode][mknodes.MkNode] is very clever. You just show him a node and he
    # will tell you all you need to know about him.
    # It's [MkDocStrings][mknodes.MkDocStrings]!
    # Lets check what he knows about [MkPage][mknodes.MkPage]:
    node = mk.MkDocStrings(mk.MkPage)
    # [MkDocStrings][mknodes.MkDocStrings] sometimes really writes long stories,
    # so we will put everything into
    # a collapsed [MkAdmonition][mknodes.MkAdmonition] box,
    # so we dont need that much space:
    admonition = mk.MkAdmonition(node, collapsible=True)
    str(admonition)
    # Here is the result:
    # {{ "mknodes.MkPage" | MkDocStrings | MkAdmonition(collapsible=True) }}

    # [MkDocStrings][mknodes.MkDocStrings] can even show information about himself.
    # Very talented!
    node = mk.MkDocStrings(mk.MkDocStrings)
    admonition = mk.MkAdmonition(node, collapsible=True)
    str(admonition)
    # {{ "mknodes.MkDocStrings" | MkDocStrings | MkAdmonition(collapsible=True)}}

    # Okay, that's enough DocStrings for today. You can find more of
    # [MkDocStrings][mknodes.MkDocStrings] work
    # in the API documentation, he will tell you something about every
    # [MkNode][mknodes.MkNode] there.
    #
    # Another [MkNode][mknodes.MkNode] who is displaying his skills in the API docs is
    # [MkClassDiagram][mknodes.MkClassDiagram].
    #
    # He's a very talented painter. Perhaps he can draw us something about
    # [MkPage][mknodes.MkPage]!
    #
    diagram = mk.MkClassDiagram(mk.MkPage)
    str(diagram)
    # {{ "mknodes.MkPage" | MkClassDiagram }}

    # [MkClassDiagram][mknodes.MkClassDiagram] can draw different kind of graphs.
    # The first picture [MkClassDiagram][mknodes.MkClassDiagram] has painted was about
    # base classes. Lets check out the subclasses:
    diagram = mk.MkClassDiagram(mk.MkPage, mode="subclasses")
    str(diagram)
    # {{ "mknodes.MkPage" | MkClassDiagram(mode="subclasses") }}

    # There are multiple talented drawers among the **MkNodes**.
    # [MkPipDepTree][mknodes.MkPipDepTree] is known for his dependency drawings,
    # we can ask him to draw a graph for one of our dependencies.
    #
    # To not overboard him, lets pick a package without too many dependencies:

    node = mk.MkPipDepTree("gitpython", direction="LR")
    str(node)
    # {{ "gitpython" | MkPipDepTree(direction="LR") }}

    # We now come to the last [MkNode][mknodes.MkNode] of our quick tour.
    #
    # Let's introduce [MkMetadataBadges][mknodes.MkMetadataBadges]!
    #
    # [MkMetadataBadges][mknodes.MkMetadataBadges] just loves Badges. He creates them
    # himself and doesnt rely on webservies.
    node = mk.MkMetadataBadges("classifiers", package="mkdocstrings")
    str(node)
    # {{ "classifiers" | MkMetadataBadges(package="mkdocstrings") }}

    # Looks neat, right?
    # This is also a good chance to explain how nodes can get their information
    # from the context. Let me explain:
    #
    # If we instanciate **MkNodes** and dont add them to the tree,
    # then the nodes are clueless. They dont know who they belong to.
    #
    # To make them part of the tree, we either add them for example to a page
    #
    # (like this: `page += node`)
    #
    # or we pass them a parent on instantiation.
    #
    # In this example, once we add [MkMetadataBadges][mknodes.MkMetadataBadges]
    # to the tree, that node knows
    # that he should create badges for our very own package, **mknodes**,
    # unless we explicitely tell him to do otherwise. It will become his new "default".
    #
    # You dont believe me? Let me show you:
    node = mk.MkMetadataBadges("websites", parent=page)

    # Now that node is connected. If we ask him to draw now, he will create website
    # badges for **mknodes**!

    str(node)
    # {{ "websites" | MkMetadataBadges }}

    # This mechanism is the same for many **MkNodes**. For example, our earlier guest
    # [MkPipDepTree][mknodes.MkPipDepTree] behaves the same. Once connected,
    # he will want to paint **mknodes** dependency graphs without us telling him to do so!
    #
    # Interesting, right?
    #
    # That's it for a first quick look at the nodes.
    # There are about 70 different ones available in this package.
    # Some are exciting, some are boring. It's no difference to humans.
    #
    # Oh, and if you wonder how this tour was done: I got help from
    # [MkCommentedCode][mknodes.MkCommentedCode]!
    #
    page += mk.MkCommentedCode(a_quick_tour, style="text")

    # [MkCommentedCode][mknodes.MkCommentedCode] parses a function and separates comments
    # from code. These chunks are displayed on a rotating basis then.
    #
    # Before we end the tour, let's take a look at the raw material.
    # We can use the [MkCode][mknodes.MkCode] node for that.
    #
    node = mk.MkCode.for_object(a_quick_tour)
    text = str(node).replace(r"{", "<").replace(r"}", ">")
    page += text
    # As you can see, we added the [MkCode][mknodes.MkCode] node to the page.
    # It will be displayed right after the [MkCommentedCode][mknodes.MkCommentedCode]
    # block. You will see it right below.
    #
    # Oh, and the String replacement you probably noticed is a quick hack to prevent
    # **jinja2** code from getting executed. YOu can ignore that, it's not relevant
    #  for this tour.
    #
    # That's it. The rest of the nodes you need to check out yourself. Have fun!
