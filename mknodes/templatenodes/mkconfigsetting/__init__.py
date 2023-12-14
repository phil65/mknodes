from __future__ import annotations

from typing import Any, TYPE_CHECKING

from mknodes.templatenodes import mktemplate

if TYPE_CHECKING:
    from mknodes.utils import superdict


class MkConfigSetting(mktemplate.MkTemplate):
    """Node for describing a config setting."""

    ICON = "material/library"

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
        super().__init__("output/markdown/template", **kwargs)
        self.title = title
        self.setting = setting
        self.default = default
        self.version_added = version_added
        self.description = description
        self.optional = optional
        self.mode = mode


if __name__ == "__main__":
    setting = {"path": {"to": "setting"}}
    desc = "Some text to describe the setting"
    node = MkConfigSetting("YAML", description=desc, setting=setting)
    print(node)
