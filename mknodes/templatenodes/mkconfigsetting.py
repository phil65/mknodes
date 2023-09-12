from __future__ import annotations

from typing import Any

from mknodes.basenodes import mkcode, mkdefinitionlist, mknode, mktext
from mknodes.utils import helpers, log, reprhelpers, superdict


logger = log.get_logger(__name__)


class MkConfigSetting(mkdefinitionlist.MkDefinition):
    """Node for describing a config setting."""

    ICON = "material/library"

    def __init__(
        self,
        title: str,
        description: str,
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

    def __repr__(self):
        return reprhelpers.get_repr(
            self,
            title=self.title,
            description=self.description,
            default=self.default,
            version_added=self.version_added,
            optional=self.optional,
            mode=self.mode,
            _filter_empty=True,
        )

    @property
    def title(self):
        return helpers.styled(self._title, bold=True, code=True)

    @property
    def items(self):
        text = f"Default: `{self.default!r}`\n\n"
        if self.version_added:
            text += f"Version added: `{self.version_added}`\n\n"
        if self.optional is not None:
            required = "no" if self.optional else "yes"
            text += f"Required: `{required}`\n\n"
        text += f"{self.description}\n"
        items: list[mknode.MkNode] = [mktext.MkText(text, parent=self)]
        if isinstance(self.setting, dict):
            code = superdict.SuperDict(self.setting).serialize(mode=self.mode)
        else:
            code = self.setting
        if self.setting:
            code_node = mkcode.MkCode(code, parent=self, language=self.mode or "yaml")
            items.append(code_node)
        return items

    @items.setter
    def items(self, value):
        pass

    @staticmethod
    def create_example_page(page):
        import mknodes

        setting = {"plugins": {"mknodes": {"path": "path.to.module"}}}
        desc = "Some **markdown** to describe the setting"
        node = MkConfigSetting(
            "path",
            setting=setting,
            description=desc,
            default="path.to.module",
        )
        page += mknodes.MkReprRawRendered(node, header="### YAML")
        node = MkConfigSetting(
            "path",
            mode="json",
            setting=setting,
            description=desc,
            default="path.to.module",
        )
        page += mknodes.MkReprRawRendered(node, header="### JSON")
        node = MkConfigSetting(
            "path",
            mode="toml",
            version_added="2.1.0",
            setting=setting,
            description=desc,
            default="path.to.module",
        )
        page += mknodes.MkReprRawRendered(node, header="### TOML")


if __name__ == "__main__":
    setting = {"path": {"to": "setting"}}
    desc = "Some text to describe the setting"
    node = MkConfigSetting("YAML", description=desc, setting=setting)
    print(node)
