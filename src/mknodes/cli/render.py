"""Render commands: Markdown files / folders with the MkNodes Jinja environment."""

from pathlib import Path
import sys

import typer as t

import mknodes as mk
from mknodes.cli.app import REPO_CMDS, REPO_HELP, cli, quiet_option, verbose_option
from mknodes.utils import log


logger = log.get_logger(__name__)

INPUT_HELP = "Input markdown file to render (use - for stdin)."
INPUT_DIR_HELP = "Input directory containing files to render."
OUTPUT_FILE_HELP = "Output file (use - for stdout, default)."
OUTPUT_DIR_HELP = "Output directory for rendered files."
GLOB_HELP = "Glob pattern for files to render as Jinja templates."
COPY_OTHER_HELP = "Copy files not matching the glob pattern as-is."
WORKERS_HELP = "Number of parallel workers for copying files."

INPUT_CMDS = "-i", "--input"
OUTPUT_CMDS = "-o", "--output"
OUTPUT_FILE_CMDS = "-o", "--output"
GLOB_CMDS = "-g", "--glob"
WORKERS_CMDS = "-w", "--workers"


@cli.command()
def render(
    input_file: str = t.Option(..., *INPUT_CMDS, help=INPUT_HELP),
    output_file: str = t.Option("-", *OUTPUT_FILE_CMDS, help=OUTPUT_FILE_HELP),
    repo_url: str | None = t.Option(None, *REPO_CMDS, help=REPO_HELP, show_default=False),
    _verbose: bool = verbose_option(),
    _quiet: bool = quiet_option(),
) -> None:
    """Render a single markdown file with Jinja macros.

    Reads markdown content, processes Jinja templates, and outputs the result.

    Example:
        mknodes render -i template.md -o output.md
        cat template.md | mknodes render -i - > output.md
    """
    _render(input_file, output_file, repo_url)


def _render(input_file: str, output_file: str, repo_url: str | None) -> None:
    """Implementation of the render command."""
    from mknodes import inputs
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
    env = nodeenvironment.create_node_environment(page)

    # Render the content
    rendered = inputs.run_passes(lambda: env.render_string(content))

    # Write output
    if output_file == "-":
        sys.stdout.write(rendered)
    else:
        Path(output_file).write_text(rendered, encoding="utf-8")
        logger.info("Rendered output written to: %s", output_file)


@cli.command()
def render_folder(
    input_dir: Path = t.Option(..., *INPUT_CMDS, help=INPUT_DIR_HELP),  # noqa: B008
    output_dir: Path = t.Option(..., *OUTPUT_CMDS, help=OUTPUT_DIR_HELP),  # noqa: B008
    repo_url: str | None = t.Option(None, *REPO_CMDS, help=REPO_HELP, show_default=False),
    glob: str = t.Option("**/*.md", *GLOB_CMDS, help=GLOB_HELP),
    copy_other: bool = t.Option(True, "--copy-other/--no-copy-other", help=COPY_OTHER_HELP),
    workers: int | None = t.Option(None, *WORKERS_CMDS, help=WORKERS_HELP),
    _verbose: bool = verbose_option(),
    _quiet: bool = quiet_option(),
) -> None:
    """Render a folder of markdown files with Jinja macros.

    Processes all files matching the glob pattern through Jinja templating,
    preserving directory structure. Non-matching files can optionally be copied as-is.

    Example:
        mknodes render-folder -i ./src/docs -o ./docs
        mknodes render-folder -i ./templates -o ./output --glob "**/*.md" --no-copy-other
    """
    _render_folder(input_dir, output_dir, repo_url, glob, copy_other, workers)


def _render_folder(
    input_dir: Path,
    output_dir: Path,
    repo_url: str | None,
    glob: str,
    copy_other: bool,
    max_workers: int | None,
) -> None:
    """Implementation of the render_folder command."""
    from concurrent.futures import ThreadPoolExecutor
    import shutil

    from mknodes import inputs
    from mknodes.jinja import nodeenvironment

    if not input_dir.exists():
        logger.error("Input directory not found: %s", input_dir)
        raise SystemExit(1)

    if not input_dir.is_dir():
        logger.error("Input path is not a directory: %s", input_dir)
        raise SystemExit(1)

    # Create context for rendering
    nav = mk.MkNav.with_context(repo_url=repo_url) if repo_url else mk.MkNav()
    page = nav.add_page("render", is_index=True)
    env = nodeenvironment.create_node_environment(page)

    # Collect files to process
    matching_files = list(input_dir.glob(glob))
    all_files = list(input_dir.rglob("*"))
    non_matching_files = [f for f in all_files if f.is_file() and f not in matching_files]
    msg = "Found %d files to render, %d other files"
    logger.info(msg, len(matching_files), len(non_matching_files))

    # Ensure output directory exists
    output_dir.mkdir(parents=True, exist_ok=True)

    def render_file(src: Path) -> None:
        """Render a single file."""
        rel_path = src.relative_to(input_dir)
        dest = output_dir / rel_path
        dest.parent.mkdir(parents=True, exist_ok=True)

        content = src.read_text(encoding="utf-8")
        rendered = inputs.run_passes(lambda: env.render_string(content))
        dest.write_text(rendered, encoding="utf-8")
        logger.debug("Rendered: %s -> %s", src, dest)

    def copy_file(src: Path) -> None:
        """Copy a single file."""
        rel_path = src.relative_to(input_dir)
        dest = output_dir / rel_path
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dest)
        logger.debug("Copied: %s -> %s", src, dest)

    # Render matching files
    for src in matching_files:
        render_file(src)

    # Copy non-matching files if requested
    if copy_other and non_matching_files:
        workers = max_workers or min(32, len(non_matching_files))
        with ThreadPoolExecutor(max_workers=workers) as executor:
            list(executor.map(copy_file, non_matching_files))

    logger.info(
        "Render complete: %d rendered, %d copied to %s",
        len(matching_files),
        len(non_matching_files) if copy_other else 0,
        output_dir,
    )
