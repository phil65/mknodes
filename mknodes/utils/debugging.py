from __future__ import annotations

import io
import os
import pathlib

from mkdocs.commands import serve
import yaml


# from mknodes import mkdocsconfig


content = """
import mknodes

def build(project):
    root = project.get_root()
    page = root.add_index_page(hide_toc=True)
    page += '''{node}'''


"""


def serve_node(node):
    text = content.format(node=str(node))

    p = pathlib.Path("docs/test.py")
    p.write_text(text)
    # file = tempfile.NamedTemporaryFile("w")
    # file.write(text)
    serve_script(p)
    # webbrowser.open("http://127.0.0.1:8000")


# def serve_script(script_file: str | os.PathLike):
#     script_file = pathlib.Path(script_file).absolute()
#     script_file = script_file.relative_to(pathlib.Path.cwd())
#     config = mkdocsconfig.Config()
#     config.scripts = [script_file.as_posix()]
#     output = yaml.dump(config._config, Dumper=yaml.Dumper)
#     print(output)
#     stream = io.StringIO(output)
#     serve.serve(
#         config_file=stream,  # type: ignore
#         dev_addr=None,
#         livereload=True,  # type: ignore
#         build_type=None,
#         watch_theme=False,
#         watch=[],
#     )


def serve_script(script_file: str | os.PathLike):
    script_file = pathlib.Path(script_file).absolute()
    script_file = script_file.relative_to(pathlib.Path.cwd())
    # path = ".".join(script_file.parts).removeprefix(".py")
    text = pathlib.Path("mkdocs.yml").read_text()
    config_file = yaml.load(text, Loader=yaml.Loader)
    for plugin in config_file["plugins"]:
        if isinstance(plugin, dict) and next(iter(plugin.keys())) == "mknodes":
            plugin["mknodes"]["path"] = str(script_file)  # path
    output = yaml.dump(config_file, Dumper=yaml.Dumper)
    stream = io.StringIO(output)
    serve.serve(
        config_file=stream,  # type: ignore
        dev_addr=None,
        livereload=True,  # type: ignore
        build_type=None,
        watch_theme=False,
        watch=[],
    )


if __name__ == "__main__":
    # import sys

    # serve_script(sys.argv[1])
    import mknodes

    test = mknodes.MkCard("a", "b", "c")
    serve_node(test)
