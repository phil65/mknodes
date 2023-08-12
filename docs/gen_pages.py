from mknodes import manual


def build(config, files):
    root = manual.create_root(config, files)
    root.write()
