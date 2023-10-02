import mknodes as mk


def a_quick_tour(page: mk.MkPage):
    # Let the tour begin! We will start by introducing some `MkNodes`.
    #
    # Our first `MkNode` is very clever. You just show him a node and he will tell
    # you all you need to know about him. It's `MkDocStrings`!
    # Lets check what he knows about `MkPages`:
    node = mk.MkDocStrings(mk.MkPage)
    # `MkDocStrings` sometimes really writes long stories, so we will put everything into
    # a collapsed `MkAdmonition` box, so we dont need that much space:
    admonition = mk.MkAdmonition(node, collapsible=True)
    str(admonition)
    # Here is the result:
    # {{ "mknodes.MkPage" | MkDocStrings | MkAdmonition(collapsible=True) }}

    # `MkDocStrings` can even show information about himself. Very talented!
    node = mk.MkDocStrings(mk.MkDocStrings)
    admonition = mk.MkAdmonition(node, collapsible=True)
    str(admonition)
    # {{ "mknodes.MkDocStrings" | MkDocStrings | MkAdmonition(collapsible=True)}}

    # Okay, that's enough DocStrings for today. You can find more of `MkDocStrings` work
    # in the API documentation, he will tell you something about every `MkNode` there.
    #
    # Another `MkNode` who is displaying his skills in the API docs is `MkClassDiagram`.
    #
    # He's a very talented painter. Perhaps he can draw us something about `MkPage`!
    #
    diagram = mk.MkClassDiagram(mk.MkPage)
    str(diagram)
    # {{ "mknodes.MkPage" | MkClassDiagram }}

    # `MkClassDiagram` can draw different kind of graphs.
    # The first picture `MkClassDiagram` has painted was about base classes.
    # Lets check out the subclasses:
    diagram = mk.MkClassDiagram(mk.MkPage, mode="subclasses")
    str(diagram)
    # {{ "mknodes.MkPage" | MkClassDiagram(mode="subclasses") }}

    # There are multiple talented drawers among the `MkNodes`.
    # `MkPipDepTree` is known for his dependency drawings, let's check out his skills!
    #
    # We can ask him to draw a graph for one of our dependencies.
    #
    # To not overboard him, lets pick a package without too many dependencies:

    node = mk.MkPipDepTree("gitpython", direction="LR")
    str(node)
    # {{ "gitpython" | MkPipDepTree(direction="LR") }}

    # We now come to the last `MkNode` of our quick tour.
    #
    # Let's introduce `MkMetadataBadges`!
    #
    # `MkMetadataBadges` just loves Badges. He creates them himself and doesnt rely on
    # webservies.
    node = mk.MkMetadataBadges("classifiers", package="mkdocstrings")
    str(node)
    # {{ "classifiers" | MkMetadataBadges(package="mkdocstrings") }}

    # Looks neat, right?
    # This is also a good chance to explain how nodes can get their information
    # from the context. Let me explain:
    #
    # If we instanciate `MkNodes` and dont add them to the tree,
    # then the nodes are clueless. They dont know who they belong to.
    #
    # To make them part of the tree, we either add them for example to a page
    #
    # (like this: `page += node`)
    #
    # or we pass them a parent on instantiation.
    #
    # In this example, once we add `MkMetadataBadges` to the tree, that node knows
    # that he should create badges for our very own package, `mknodes`,
    # unless we explicitely tell him to do otherwise. It will become his new "default".
    #
    # You dont believe me? Let me show you:
    node = mk.MkMetadataBadges("websites", parent=page)

    # Now that node is connected. If we ask him to draw now, he will create website
    # badges for `mknodes`!

    str(node)
    # {{ "websites" | MkMetadataBadges }}

    # This mechanism is the same for many `MkNodes`. For example, our earlier guest
    # `MkPipDepTree` behaves the same. Once connected, he will want to paint `mknodes`
    # dependency graphs without us telling him to do so!
    #
    # Interesting, right?
    #
    # That's it for a first quick look at the nodes.
    # There are about 70 different ones available in this package.
    # Some are exciting, some are boring. It's no difference to humans.
    #
    # Oh, and if you wonder how this tour was done: I got help from `MkCommentedCode`!

    page += mk.MkCommentedCode(a_quick_tour, style="text")

    # `MkCommentedCode` parses a function and separates comments from code.
    # These chunks are displayed on a rotating basis then.

    # That's it. The rest of the nodes you need to check out yourself. Have fun!
    print("bye!")
