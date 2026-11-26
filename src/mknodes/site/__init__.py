"""Engine-agnostic site generator.

Runs a MkNodes build function, collects the result into an engine-neutral
`BuildOutput` (`mknodes.build`) and lets a writer
(see `mknodes.site.writers`) produce the input files for a site engine.
"""

from typing import TYPE_CHECKING, Any

from mknodes.build import BuildOutput, NavItem, Script, SiteMetadata
from mknodes.site.defaultsite import MkDefaultWebsite, parse
from mknodes.site.settings import GeneratorSettings


if TYPE_CHECKING:
    import pathlib

    from mknodes.rendering import Renderer


def generate_output(
    settings: GeneratorSettings, flavor: str | Renderer | None = None
) -> BuildOutput:
    """Run the build function of given settings and return the collected output.

    Args:
        settings: Generator settings
        flavor: Markdown flavour or renderer (default: the `flavor` setting, else `material`)
    """
    from mknodes.site.generator import SiteGenerator

    return SiteGenerator(settings, flavor=flavor).generate()


def generate(
    settings: GeneratorSettings | None = None,
    engine: str = "zensical",
    **overrides: Any,
) -> pathlib.Path:
    """Generate the site input for given engine. Returns the config file to build with.

    Args:
        settings: Generator settings (default: loaded from the current folder)
        engine: Name of the writer to use
        overrides: Setting overrides used when settings get loaded
    """
    from mknodes.site.writers import get_writer

    settings = settings or GeneratorSettings.load(**overrides)
    writer = get_writer(engine)(settings)
    output = generate_output(settings, flavor=writer.get_renderer())
    return writer.write(output)


__all__ = [
    "BuildOutput",
    "GeneratorSettings",
    "MkDefaultWebsite",
    "NavItem",
    "Script",
    "SiteMetadata",
    "generate",
    "generate_output",
    "parse",
]
