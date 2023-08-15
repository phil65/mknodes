from __future__ import annotations

import io
import os
import pathlib

from mkdocs.commands import serve
import yaml

from mknodes import mkdocsconfig


def serve_script(script_file: str | os.PathLike):
    script_file = pathlib.Path(script_file).absolute()
    script_file = script_file.relative_to(pathlib.Path.cwd())
    config = mkdocsconfig.Config()
    config.scripts = [script_file.as_posix()]
    output = yaml.dump(config._config, Dumper=yaml.Dumper)
    stream = io.StringIO(output)
    serve.serve(
        config_file=stream,  # type: ignore
        dev_addr=None,
        livereload="livereload",  # type: ignore
        build_type=None,
        watch_theme=False,
        watch=[],
    )


if __name__ == "__main__":
    import sys

    serve_script(sys.argv[1])
