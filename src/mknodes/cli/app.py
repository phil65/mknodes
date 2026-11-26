"""The MkNodes Typer app and options shared by all commands."""

import logging

import typer as t

from mknodes.cli import richstate


cli = t.Typer(
    name="mknodes",
    help=(
        "MkNodes: build documentation from Python node trees.\n\n"
        "`generate` writes the pages (and the site config), `build` / `serve` also run the "
        "site engine. Docs: https://phil65.github.io/mknodes/"
    ),
    no_args_is_help=True,
    # Help texts are Markdown (`code`) with literal brackets (`[tool.mknodes]`).
    rich_markup_mode="markdown",
)

VERBOSE_HELP = "Enable verbose output. (`DEBUG` level)"
QUIET_HELP = "Suppress output."
REPO_HELP = "Repository URL of the target package. Can be remote or local."
VERBOSE_CMDS = "-v", "--verbose"
QUIET_CMDS = "-q", "--quiet"
REPO_CMDS = "-r", "--repo-url"


def verbose(ctx: t.Context, _param: t.CallbackParam, value: bool) -> None:
    state = ctx.ensure_object(richstate.RichState)
    if value:
        state.set_level(logging.DEBUG)


def quiet(ctx: t.Context, _param: t.CallbackParam, value: bool) -> None:
    state = ctx.ensure_object(richstate.RichState)
    if value:
        state.set_level(logging.ERROR)


def verbose_option() -> bool:
    return t.Option(False, *VERBOSE_CMDS, help=VERBOSE_HELP, callback=verbose)


def quiet_option() -> bool:
    return t.Option(False, *QUIET_CMDS, help=QUIET_HELP, callback=quiet)
