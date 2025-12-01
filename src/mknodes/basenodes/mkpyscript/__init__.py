from __future__ import annotations

from typing import Any

from mknodes.basenodes import mknode
from mknodes.utils import log
from mknodes.utils import resources


logger = log.get_logger(__name__)


class MkPyScript(mknode.MkNode):
    """Node for embedding a PyScript terminal."""

    ICON = "material/console"

    # Core PyScript files
    CSS = [resources.CSSFile("https://pyscript.net/releases/2025.2.2/core.css")]
    JS_FILES = [resources.JSFile("https://pyscript.net/releases/2025.2.2/core.js")]

    def __init__(
        self,
        code: str = "",
        *,
        packages: list[str] | None = None,
        height: str = "400px",
        width: str = "100%",
        **kwargs: Any,
    ) -> None:
        """Constructor.

        Args:
            code: Python code to run
            packages: List of packages to pre-install
            height: Terminal height (CSS value)
            width: Terminal width (CSS value)
            kwargs: Keyword arguments passed to parent
        """
        super().__init__(**kwargs)
        self.code = code
        self.packages = packages or []
        self.height = height
        self.width = width

    async def to_md_unprocessed(self) -> str:
        packages_str = ", ".join(repr(pkg) for pkg in self.packages)
        html = f"""
<div style="height: {self.height}; width: {self.width};">
    <py-config>
        packages = [{packages_str}]
    </py-config>
    <py-script>
{self.code}
    </py-script>
</div>
"""
        return "\n\n" + html + "\n\n"


if __name__ == "__main__":
    # Example usage in your documentation pages:
    terminal = MkPyScript("""
        from llmling_textual.creator import ConfigGeneratorApp
        app = ConfigGeneratorApp()
        app.run()
    """)
    print(terminal.to_markdown())
