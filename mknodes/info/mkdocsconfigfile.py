from __future__ import annotations

from mknodes.info import yamlfile


class MkDocsConfigFile(yamlfile.YamlFile):
    @property
    def theme(self):
        return self.get_section("theme")

    @property
    def markdown_extensions(self):
        return self.get_section("markdown_extensions")

    @property
    def plugins(self):
        return self.get_section("plugins")

    @property
    def mknodes_config(self):
        return self.get_section("plugins", "mknodes")

    @property
    def mkdocstrings_config(self):
        return self.get_section("plugins", "mkdocstrings", "handlers", "python")


if __name__ == "__main__":
    info = MkDocsConfigFile("mkdocs.yml")
    print(info.mkdocstrings_config)
