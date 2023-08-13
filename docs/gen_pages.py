from mknodes import manual


def build(project):
    root = manual.create_root(project)
    root.write()
