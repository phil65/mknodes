from __future__ import annotations

import contextlib
import pathlib
import shutil
import tempfile

from typing import TYPE_CHECKING
from urllib.parse import urlsplit

import jinja2.exceptions

from mkdocs.commands.build import build
from mkdocs.config import load_config
from mkdocs.exceptions import Abort
from mkdocs.livereload import LiveReloadServer

from mknodes.utils import log


if TYPE_CHECKING:
    from mkdocs.config.defaults import MkDocsConfig

logger = log.get_logger(__name__)


@contextlib.contextmanager
def catch_exceptions(config, site_dir):
    try:
        yield
    except jinja2.exceptions.TemplateError:
        # This is a subclass of OSError, but shouldn't be suppressed.
        raise
    except OSError as e:  # pragma: no cover
        # Avoid ugly, unhelpful traceback
        msg = f"{type(e).__name__}: {e}"
        raise Abort(msg) from e
    finally:
        config.plugins.on_shutdown()
        if pathlib.Path(site_dir).is_dir():
            shutil.rmtree(site_dir)


def serve(
    config_file: str | None = None,
    livereload: bool = True,
    build_type: str | None = None,
    watch_theme: bool = False,
    watch: list[str] | None = None,
    **kwargs,
) -> None:
    """Start the MkDocs development server.

    By default it will serve the documentation on http://localhost:8000/ and
    it will rebuild the documentation and refresh the page automatically
    whenever a file is edited.
    """
    watch = watch or []
    site_dir = tempfile.mkdtemp(prefix="mkdocs_")

    def mount_path(config: MkDocsConfig):
        return urlsplit(config.site_url or "/").path

    def get_config():
        config = load_config(config_file=config_file, site_dir=site_dir, **kwargs)
        config.watch.extend(watch)
        config.site_url = f"http://{config.dev_addr}{mount_path(config)}"
        return config

    is_clean = build_type == "clean"
    is_dirty = build_type == "dirty"

    config = get_config()
    config.plugins.on_startup(command=("build" if is_clean else "serve"), dirty=is_dirty)

    def builder(config: MkDocsConfig | None = None):
        logger.info("Building documentation...")
        if config is None:
            config = get_config()
        build(config, live_server=None if is_clean else server, dirty=is_dirty)

    # Perform the initial build
    with catch_exceptions(config, site_dir):
        builder(config)

    host, port = config.dev_addr
    server = LiveReloadServer(
        builder=builder,
        host=host,
        port=port,
        root=site_dir,
        mount_path=mount_path(config),
    )

    def error_handler(code) -> bytes | None:
        if code not in (404, 500):
            return None
        error_page = pathlib.Path(site_dir) / f"{code}.html"
        if not error_page.is_file():
            return None
        with error_page.open("rb") as f:
            return f.read()

    # Run the server
    server.error_handler = error_handler
    with catch_exceptions(config, site_dir):
        run_server(server, config, builder, livereload, watch_theme)


def run_server(server, config, builder, livereload, watch_theme):
    if livereload:
        # Watch the documentation files, the config file and the theme files.
        server.watch(config.docs_dir)
        if config.config_file_path:
            server.watch(config.config_file_path)

        if watch_theme:
            for d in config.theme.dirs:
                server.watch(d)

        # Run `serve` plugin events.
        server = config.plugins.on_serve(server, config=config, builder=builder)

        for item in config.watch:
            server.watch(item)

    try:
        server.serve()
    except KeyboardInterrupt:
        logger.info("Shutting down...")
    finally:
        server.shutdown()
