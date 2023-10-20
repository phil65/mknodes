from __future__ import annotations

import ast
import datetime
import functools

from importlib import util
import json
import os
import time
import tomllib
from typing import Any

import tomli_w

from mknodes import paths
from mknodes.utils import helpers, icons, inspecthelpers, log, pathhelpers, yamlhelpers


logger = log.get_logger(__name__)


def evaluate(
    text: str,
    context: dict[str, Any] | None = None,
    return_val: str | None = None,
):
    """Evaluate several lines of input, returning the result of the last line."""
    now = time.time()
    if context is None:
        context = locals()
    code = str(text) if return_val is None else f"{text}\n{return_val}"
    logger.debug("Evaluating code:\n%s", text)
    tree = ast.parse(code)
    eval_expr = ast.Expression(tree.body[-1].value)  # type: ignore
    # exec_expr = ast.Module(tree.body[:-1])  # type: ignore
    exec_expr = ast.parse("")
    exec_expr.body = tree.body[:-1]
    compiled = compile(exec_expr, "file", "exec")
    exec(compiled, context)
    val = eval(compile(eval_expr, "file", "eval"), context)
    logger.debug("Code evaluation took %s seconds.", time.time() - now)
    return val


ENV_GLOBALS = {
    "log": log.log_stream.getvalue,
    "now": datetime.datetime.now,
    "str": str,
    "inspecthelpers": inspecthelpers,
    "resources_dir": paths.RESOURCES,
}
ENV_FILTERS = {
    "get_icon_svg": icons.get_icon_svg,
    "styled": helpers.styled,
    "str": str,
    "rstrip": str.rstrip,
    "lstrip": str.lstrip,
    "removesuffix": str.removesuffix,
    "removeprefix": str.removeprefix,
    "issubclass": issubclass,
    "isinstance": isinstance,
    "hasattr": hasattr,
    "evaluate": evaluate,
    "partial": functools.partial,
    "dump_yaml": yamlhelpers.dump_yaml,
    "dump_json": json.dumps,
    "dump_toml": tomli_w.dumps,
    "load_json": json.loads,
    "joad_toml": tomllib.loads,
    "load_yaml": yamlhelpers.load_yaml,
    "load_file": pathhelpers.load_file_cached,
    "path_join": os.path.join,
}


def set_markdown_exec_namespace(variables: dict[str, Any], namespace: str = "mknodes"):
    if util.find_spec("markdown_exec"):
        from markdown_exec.formatters import python

        python._sessions_globals[namespace] = variables


if __name__ == "__main__":
    a = evaluate("import mknodes\nmknodes.MkHeader('Hello')")
    print(a)
