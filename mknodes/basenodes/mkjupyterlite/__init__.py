from __future__ import annotations

from typing import Any
from urllib.parse import quote

from mknodes.basenodes import mknode
from mknodes.utils import log


logger = log.get_logger(__name__)


class MkJupyterLite(mknode.MkNode):
    """Node for embedding a JupyterLite RetroLab interface."""

    ICON = "material/notebook"

    def __init__(
        self,
        code: str = "",
        *,
        height: str = "400px",
        width: str = "100%",
        **kwargs: Any,
    ):
        super().__init__(**kwargs)
        self.code = code
        self.height = height
        self.width = width

    def _to_markdown(self) -> str:
        encoded_code = quote(self.code)
        html = f"""
<iframe
    src="https://jupyterlite.github.io/demo/repl/index.html?kernel=python&code={encoded_code}"
    width="{self.width}"
    height="{self.height}"
    style="border: none;">
</iframe>
"""
        return "\n\n" + html + "\n\n"


if __name__ == "__main__":
    # Example usage in your documentation pages:
    terminal = MkJupyterLite("""
        from llmling_textual.creator import ConfigGeneratorApp
        app = ConfigGeneratorApp()
        app.run()
    """)
    print(terminal.to_markdown())
