from __future__ import annotations

from typing import TYPE_CHECKING, Any

from mknodes.navs import mknav
from mknodes.pages import mkpage
from mknodes.utils import log, reprhelpers


if TYPE_CHECKING:
    import argparse

    import clinspector


logger = log.get_logger(__name__)


class MkCliNav(mknav.MkNav):
    """Nav for showing CLI documentation for click/typer/argparse apps."""

    ICON = "material/console"

    def __init__(
        self,
        target: str | argparse.ArgumentParser | None = None,
        *,
        prog_name: str | None = None,
        show_hidden: bool = False,
        recursive: bool = True,
        section_name: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Constructor.

        Args:
            target: Dotted path to click group / typer instance / ArgumentParser
            prog_name: Program name (uses entry point name if None)
            show_hidden: Show commands marked as hidden
            recursive: Recursively create navs for nested subcommands
            section_name: Optional section title override
            kwargs: Keyword arguments passed to parent
        """
        self.target = target
        self.prog_name = prog_name
        self.show_hidden = show_hidden
        self.recursive = recursive
        self._section_name = section_name
        self._cli_info: clinspector.CommandInfo | None = None
        super().__init__(section=section_name, **kwargs)

    def __repr__(self) -> str:
        return reprhelpers.get_repr(
            self,
            target=self.target,
            prog_name=self.prog_name,
            section=self.title or "<root>",
        )

    @property
    def cli_info(self) -> clinspector.CommandInfo | None:
        """Return CLI info for the target."""
        if self._cli_info is not None:
            return self._cli_info

        import importlib

        import clinspector

        match self.target:
            case str():
                module, command = self.target.split(":")
                mod = importlib.import_module(module)
                instance = getattr(mod, command)
                self._cli_info = clinspector.get_cmd_info(instance, command=self.prog_name)
            case None:
                if cli_eps := self.ctx.metadata.entry_points.get_group("console_scripts"):
                    module, command = cli_eps[0].value.split(":")
                    prog_name = self.prog_name or cli_eps[0].name
                    mod = importlib.import_module(module)
                    instance = getattr(mod, command)
                    self._cli_info = clinspector.get_cmd_info(instance, command=prog_name)
                else:
                    return None
            case _:
                self._cli_info = clinspector.get_cmd_info(self.target, command=self.prog_name)

        return self._cli_info

    def get_children(self):
        """Return computed children for CLI documentation."""
        if self.cli_info is None:
            return []

        children: list[mknav.MkNav | mkpage.MkPage] = []

        # Create index page with command overview
        index_page = self._create_index_page()
        self.index_page = index_page

        # Create pages/navs for subcommands
        for name, subcmd_info in self.cli_info.subcommands.items():
            if subcmd_info.hidden and not self.show_hidden:
                continue

            if self.recursive and subcmd_info.subcommands:
                # Create nested nav for commands with subcommands
                subnav = MkCliNav(
                    target=self.target,
                    prog_name=name,
                    show_hidden=self.show_hidden,
                    recursive=self.recursive,
                    section_name=name,
                    parent=self,
                )
                subnav._cli_info = subcmd_info
                self.nav.register(subnav)
                children.append(subnav)
            else:
                # Create page for leaf commands
                page = self._create_command_page(name, subcmd_info)
                self.nav.register(page)
                children.append(page)

        return [*children, index_page]

    def _create_index_page(self) -> mkpage.MkPage:
        """Create index page with command table."""
        import mknodes as mk

        title = self._section_name or (self.cli_info.name if self.cli_info else "CLI")
        page = mkpage.MkPage(
            title=title,
            is_index=True,
            parent=self,
        )

        if self.cli_info is None:
            return page

        if self.cli_info.description:
            page += mk.MkText(self.cli_info.description)

        # Add usage if available
        if self.cli_info.usage:
            page += mk.MkHeader("Usage", level=2)
            page += mk.MkCode(self.cli_info.usage, language="")

        # Create table of subcommands
        if self.cli_info.subcommands:
            page += mk.MkHeader("Commands", level=2)
            table_data = []
            for name, subcmd in self.cli_info.subcommands.items():
                if subcmd.hidden and not self.show_hidden:
                    continue
                # Use folder path for nested navs, .md for leaf pages
                has_subcommands = self.recursive and subcmd.subcommands
                link_path = f"{name}/" if has_subcommands else f"{name}.md"
                table_data.append({
                    "Command": f"[`{name}`]({link_path})",
                    "Description": subcmd.description or "",
                })
            if table_data:
                page += mk.MkTable(table_data, columns=["Command", "Description"])  # type: ignore[arg-type]

        return page

    def _create_command_page(self, name: str, cmd_info: clinspector.CommandInfo) -> mkpage.MkPage:
        """Create a page for a single command."""
        import mknodes as mk

        page = mkpage.MkPage(
            title=name,
            path=f"{name}.md",
            parent=self,
        )

        # Add MkCliDoc for detailed documentation
        page += mk.MkCliDoc(
            self.target,
            prog_name=name,
            show_hidden=self.show_hidden,
        )

        return page


if __name__ == "__main__":
    nav = MkCliNav("mkdocs_mknodes.cli:cli")
    print(nav)
