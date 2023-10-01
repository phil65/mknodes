from __future__ import annotations

from mknodes.info import yamlfile


class MkDocsConfigFile(yamlfile.YamlFile):
    @property
    def theme(self):
        """Return theme section."""
        return self.get_section("theme")

    @property
    def markdown_extensions(self) -> list:
        """Return a list of markdown extensions."""
        return self.get_section("markdown_extensions") or []

    @property
    def plugins(self) -> list:
        """Return a list of plugins from the config."""
        return self.get_section("plugins") or []

    @property
    def mknodes_config(self) -> dict | None:
        """Return our very own config section."""
        return self.get_section("plugins", "mknodes")

    @property
    def mkdocstrings_config(self) -> dict:
        """Return the MkDocStrings config section."""
        return self.get_section("plugins", "mkdocstrings", "handlers", "python") or {}

    def update_mknodes_section(
        self,
        repo_url: str | None = None,
        build_fn: str | None = None,
        clone_depth: int | None = None,
    ):
        """Quick access to overriding our plugin settings.

        Arguments:
            repo_url: Repo url to set
            build_fn: Build function to set
            clone_depth: Amount of commits to fetch when cloning a repository.
        """
        for plugin in self._data["plugins"]:
            if "mknodes" in plugin:
                if repo_url is not None:
                    plugin["mknodes"]["repo_path"] = repo_url
                if build_fn is not None:
                    plugin["mknodes"]["build_fn"] = build_fn
                if clone_depth is not None:
                    plugin["mknodes"]["clone_depth"] = clone_depth

    def get_inventory_infos(self) -> list[dict]:
        """Returns list of dicts containing inventory info.

        Shape: [{"url": inventory_url, "domains": ["std", "py"]}, ...]
        """
        return self.mkdocstrings_config.get("import") or []

    @property
    def theme_name(self) -> str:
        """Name of currently used theme."""
        try:
            return self._data["theme"]["name"]
        except (KeyError, TypeError):
            return self._data["theme"]


if __name__ == "__main__":
    info = MkDocsConfigFile("mkdocs.yml")
    print(info.mkdocstrings_config)
