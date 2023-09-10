from __future__ import annotations

import logging

import click

from mkdocs import __main__ as mkdocs


repo_url_option = click.option(
    "-r",
    "--repo-url",
    help="Repo url of package to create a website for.",
)

site_script_option = click.option(
    "-s",
    "--site-script",
    help="Path to script used for building website.",
    default="mknodes.mkwebsite:MkWebSite.for_project",
)

site_dir_option = click.option(
    "-d",
    "--site-dir",
    help="Directory to create the website in.",
)
clone_depth_option = click.option(
    "-c",
    "--clone-depth",
    help="How many commits to fetch if repository is remote.",
    type=int,
    default=100,
)

config_path_option = click.option(
    "-p",
    "--config-path",
    help="Path where config file should get written to.",
    default="mknodes.mkwebsite:MkWebSite.for_project",
)

theme_option = click.option(
    "-t",
    "--theme",
    type=click.Choice(mkdocs.theme_choices),
    help="Theme to use",
)

use_directory_urls_option = click.option(
    "--use-directory-urls/--no-directory-urls",
    is_flag=True,
    default=None,
    help=mkdocs.use_directory_urls_help,
)

strict_option = click.option(
    "-s",
    "--strict/--no-strict",
    is_flag=True,
    default=None,
    help=mkdocs.strict_help,
)


def verbose_callback(ctx, param, value):
    state = ctx.ensure_object(mkdocs.State)
    if value:
        state.stream.setLevel(logging.DEBUG)


def quiet_callback(ctx, param, value):
    state = ctx.ensure_object(mkdocs.State)
    if value:
        state.stream.setLevel(logging.ERROR)


verbose_option = click.option(
    "-v",
    "--verbose",
    is_flag=True,
    expose_value=False,
    help="Enable verbose output",
    callback=verbose_callback,
)


quiet_option = click.option(
    "-q",
    "--quiet",
    is_flag=True,
    expose_value=False,
    help="Silence warnings",
    callback=quiet_callback,
)
