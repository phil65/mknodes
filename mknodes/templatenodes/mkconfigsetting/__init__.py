from __future__ import annotations

from typing import Any

from mknodes.basenodes import mkdefinitionlist
from mknodes.utils import helpers, log, superdict


logger = log.get_logger(__name__)


class MkConfigSetting(mkdefinitionlist.MkDefinition):
    """Node for describing a config setting."""

    ICON = "material/library"
    VIRTUAL_CHILDREN = True

    def __init__(
        self,
        title: str,
        description: str,
        *,
        setting: dict[str, Any] | str | None = None,
        default: str | int | None = None,
        version_added: str | None = None,
        optional: bool | None = None,
        mode: superdict.MarkupTypeStr | None = None,
        **kwargs: Any,
    ):
        """Constructor.

        Arguments:
            title: Setting title
            description: Setting description
            setting: (Nested) json-like object representing the setting
            default: Default setting value
            version_added: Version added
            optional: Whether setting is optional. (None hides the label)
            mode: Markup language of settings file
            kwargs: Keyword arguments passed to parent
        """
        super().__init__(content=None, title=title, **kwargs)
        self.setting = setting
        self.default = default
        self.version_added = version_added
        self.description = description
        self.optional = optional
        self.mode = mode

    @property
    def title(self) -> str:
        return helpers.styled(self._title, bold=True, code=True)

    @property
    def setting_string(self) -> str | None:
        if isinstance(self.setting, dict):
            return superdict.SuperDict(self.setting).serialize(mode=self.mode)
        return self.setting

    @property
    def items(self):
        import mknodes as mk

        text = f"Default: `{self.default!r}`\n\n"
        if self.version_added:
            text += f"Version added: `{self.version_added}`\n\n"
        if self.optional is not None:
            required = "no" if self.optional else "yes"
            text += f"Required: `{required}`\n\n"
        text += f"{self.description}\n"
        items: list[mk.MkNode] = [mk.MkText(text, parent=self)]
        if self.setting_string:
            code_node = mk.MkCode(self.setting_string, parent=self, language=self.mode)
            items.append(code_node)
        return items

    @items.setter
    def items(self, value):
        pass

    @classmethod
    def create_example_page(cls, page):
        import mknodes as mk

        setting = {"plugins": {"mknodes": {"path": "path.to.module"}}}
        desc = "Some **markdown** to describe the setting"
        node = MkConfigSetting(
            "path",
            setting=setting,
            description=desc,
            default="path.to.module",
        )
        page += mk.MkReprRawRendered(node, header="### YAML")
        node = MkConfigSetting(
            "path",
            mode="json",
            setting=setting,
            description=desc,
            default="path.to.module",
        )
        page += mk.MkReprRawRendered(node, header="### JSON")
        node = MkConfigSetting(
            "path",
            mode="toml",
            version_added="2.1.0",
            setting=setting,
            description=desc,
            default="path.to.module",
        )
        page += mk.MkReprRawRendered(node, header="### TOML")


if __name__ == "__main__":
    setting = {"path": {"to": "setting"}}
    desc = "Some text to describe the setting"
    node = MkConfigSetting("YAML", description=desc, setting=setting)
    print(node)
