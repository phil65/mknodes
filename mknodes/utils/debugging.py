from __future__ import annotations

import io
import os
import pathlib

from mkdocs.commands import serve
import yaml


def serve_script(script_file: str | os.PathLike):
    script_file = pathlib.Path(script_file).absolute()
    script_file = script_file.relative_to(pathlib.Path.cwd())
    text = pathlib.Path("mkdocs.yml").read_text()
    config_file = yaml.load(text, Loader=yaml.Loader)
    for plugin in config_file["plugins"]:
        if isinstance(plugin, dict) and next(iter(plugin.keys())) == "gen-files":
            plugin["gen-files"]["scripts"] = [script_file.as_posix()]
    output = yaml.dump(config_file, Dumper=yaml.Dumper)
    stream = io.StringIO(output)
    serve.serve(
        config_file=stream,
        dev_addr=None,
        livereload="livereload",
        build_type=None,
        watch_theme=False,
        watch=[],
    )


if __name__ == "__main__":
    import sys

    serve_script(sys.argv[1])
