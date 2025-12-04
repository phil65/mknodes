"""MkNodes CLI interface."""

from __future__ import annotations

import asyncio
import logging
import sys
from pathlib import Path

import jinjarope
import typer as t

from mknodes.utils import classhelpers, log
import mknodes as mk
from mknodes.info import contexts, folderinfo, reporegistry
from mknodes.info.linkprovider import LinkProvider


logger = log.get_logger(__name__)

cli = t.Typer(
    name="mknodes",
    help="MkNodes CLI - Generate markdown documentation from Python code.",
    no_args_is_help=True,
)


SCRIPT_HELP = "Path to build script (format: `path.to.module:function`)."
OUTPUT_HELP = "Output directory for generated markdown files."
REPO_HELP = "Repository URL or local path for context."
RENDER_JINJA_HELP = "Render Jinja templates in pages."
VERBOSE_HELP = "Enable verbose output (DEBUG level)."
QUIET_HELP = "Suppress output during build."
INPUT_HELP = "Input markdown file to render (use - for stdin)."
OUTPUT_FILE_HELP = "Output file (use - for stdout, default)."
WORKERS_HELP = "Number of parallel workers for page processing. Set PYTHON_GIL=0 for best performance with Python 3.14t."

SCRIPT_CMDS = "-s", "--script"
OUTPUT_CMDS = "-o", "--output"
REPO_CMDS = "-r", "--repo-url"
VERBOSE_CMDS = "-v", "--verbose"
QUIET_CMDS = "-q", "--quiet"
INPUT_CMDS = "-i", "--input"
OUTPUT_FILE_CMDS = "-o", "--output"
WORKERS_CMDS = "-w", "--workers"


def verbose_callback(ctx: t.Context, _param: t.CallbackParam, value: bool) -> None:
    if value:
        logging.getLogger("mknodes").setLevel(logging.DEBUG)


def quiet_callback(ctx: t.Context, _param: t.CallbackParam, value: bool) -> None:
    if value:
        logging.getLogger("mknodes").setLevel(logging.ERROR)


@cli.command()
def build(
    script: str = t.Option(..., *SCRIPT_CMDS, help=SCRIPT_HELP),
    output: Path = t.Option(Path("docs"), *OUTPUT_CMDS, help=OUTPUT_HELP),  # noqa: B008
    repo_url: str | None = t.Option(None, *REPO_CMDS, help=REPO_HELP, show_default=False),
    render_jinja: bool = t.Option(True, "--render-jinja/--no-render-jinja", help=RENDER_JINJA_HELP),
    workers: int | None = t.Option(None, *WORKERS_CMDS, help=WORKERS_HELP),
    _verbose: bool = t.Option(False, *VERBOSE_CMDS, help=VERBOSE_HELP, callback=verbose_callback),
    _quiet: bool = t.Option(False, *QUIET_CMDS, help=QUIET_HELP, callback=quiet_callback),
) -> None:
    """Build markdown documentation from a build script.

    The build script should be a function that takes a root MkNav and populates it.

    For best parallel performance with Python 3.14t (free-threaded), run with:
        PYTHON_GIL=0 mknodes build -s mypackage.docs:build

    Example:
        mknodes build -s mypackage.docs:build -o ./docs
    """
    asyncio.run(_build_async(script, output, repo_url, render_jinja, workers))


async def _build_async(
    script: str,
    output: Path,
    repo_url: str | None,
    render_jinja: bool,
    max_workers: int | None,
) -> None:
    """Async implementation of build command."""
    from mknodes.build import DocBuilder, MarkdownExporter

    logger.info("Loading build script: %s", script)
    build_fn = classhelpers.to_callable(script)

    linkprovider = LinkProvider(
        base_url="",
        use_directory_urls=True,
        include_stdlib=True,
    )
    theme = mk.Theme.get_theme(theme_name="material")
    git_repo = reporegistry.get_repo(".", clone_depth=50)
    assert theme
    info = folderinfo.FolderInfo(git_repo.working_dir)
    context = contexts.ProjectContext(
        metadata=info.context,
        git=info.git.context,
        # github=info.github.context,
        theme=theme.context,
        links=linkprovider,
        env_config=jinjarope.EnvConfig(loader=contexts.DEFAULT_LOADER),
    )
    root = mk.MkNav(context=context)

    logger.info("Executing build script...")
    result = build_fn(root)

    # Handle both styles: function modifies root in-place, or returns new nav
    if result is not None:
        root = result

    logger.info("Building documentation tree...")
    builder = DocBuilder(render_jinja=render_jinja, max_workers=max_workers)
    build_output = await builder.build(root)

    logger.info("Exporting to %s...", output)
    exporter = MarkdownExporter()
    await exporter.export(build_output, output)

    logger.info(
        "Build complete: %d files, %d pages",
        len(build_output.files),
        build_output.page_count,
    )


@cli.command()
def render(
    input_file: str = t.Option(..., *INPUT_CMDS, help=INPUT_HELP),
    output_file: str = t.Option("-", *OUTPUT_FILE_CMDS, help=OUTPUT_FILE_HELP),
    repo_url: str | None = t.Option(None, *REPO_CMDS, help=REPO_HELP, show_default=False),
    _verbose: bool = t.Option(False, *VERBOSE_CMDS, help=VERBOSE_HELP, callback=verbose_callback),
    _quiet: bool = t.Option(False, *QUIET_CMDS, help=QUIET_HELP, callback=quiet_callback),
) -> None:
    """Render a single markdown file with Jinja macros.

    Reads markdown content, processes Jinja templates, and outputs the result.

    Example:
        mknodes render -i template.md -o output.md
        cat template.md | mknodes render -i - > output.md
    """
    asyncio.run(_render_async(input_file, output_file, repo_url))


async def _render_async(input_file: str, output_file: str, repo_url: str | None) -> None:
    """Async implementation of render command."""
    from mknodes.jinja import nodeenvironment

    # Read input
    if input_file == "-":
        content = sys.stdin.read()
    else:
        path = Path(input_file)
        if not path.exists():
            logger.error("Input file not found: %s", input_file)
            raise SystemExit(1)
        content = path.read_text(encoding="utf-8")

    logger.info("Rendering markdown with Jinja macros...")

    # Create a page to hold the content and provide context
    nav = mk.MkNav.with_context(repo_url=repo_url) if repo_url else mk.MkNav()

    page = nav.add_page("render", is_index=True)
    env = nodeenvironment.NodeEnvironment(node=page)

    # Render the content
    rendered = await env.render_string_async(content)

    # Write output
    if output_file == "-":
        sys.stdout.write(rendered)
    else:
        Path(output_file).write_text(rendered, encoding="utf-8")
        logger.info("Rendered output written to: %s", output_file)


def main() -> None:
    """Entry point for CLI."""
    log.basic()
    cli()


if __name__ == "__main__":
    main()
