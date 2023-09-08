from __future__ import annotations

import dataclasses

from mknodes.utils import log


logger = log.get_logger(__name__)


@dataclasses.dataclass
class EventPlugin:
    flow: list[str]
    help_link: str
    hook_fn_path: str


MKDOCS_FLOW = [
    "on_startup",
    "on_shutdown",
    "on_serve",
    "on_config",
    "on_pre_build",
    "on_files",
    "on_nav",
    "on_env",
    "on_post_build",
    "on_build_error",
    "on_pre_template",
    "on_template_context",
    "on_post_template",
    "on_pre_page",
    "on_page_read_source",
    "on_page_markdown",
    "on_page_content",
    "on_page_context",
    "on_post_page",
    "on_post_build",
    "on_serve",
    "on_shutdown",
]


mkdocs_plugin = EventPlugin(
    flow=MKDOCS_FLOW,
    help_link="https://www.mkdocs.org/dev-guide/plugins/#{event}",
    hook_fn_path="mkdocs.plugins.BasePlugin.{event}",
)
