from __future__ import annotations

from typing import Any

from mknodes.basenodes import mknode
from mknodes.utils import log, resources


logger = log.get_logger(__name__)

XTERM_CSS = "https://cdn.jsdelivr.net/npm/xterm/css/xterm.css"
XTERM_JS = "https://cdn.jsdelivr.net/npm/xterm/lib/xterm.js"
XTERM_FIT = "https://cdn.jsdelivr.net/npm/xterm-addon-fit/lib/xterm-addon-fit.js"
PYODIDE_JS = "https://cdn.jsdelivr.net/pyodide/v0.24.1/full/pyodide.js"

INIT_SCRIPT = """
class PyodideTerminal {
    constructor(element, code) {
        this.term = new Terminal({
            cols: 80,
            rows: 24,
            theme: { background: '#1a1a1a', foreground: '#ffffff' }
        });
        this.fitAddon = new FitAddon.FitAddon();
        this.term.loadAddon(this.fitAddon);
        this.term.open(element);
        this.fitAddon.fit();
        this.code = code;
        this.initPyodide();
    }

    async initPyodide() {
        this.pyodide = await loadPyodide({
            stdout: (text) => this.term.write(text),
            stderr: (text) => this.term.write(`\x1b[31m${text}\x1b[0m`)
        });
        await this.pyodide.loadPackage(['micropip']);
        const micropip = this.pyodide.pyimport('micropip');
        await micropip.install('llmling-agent');
        await micropip.install('textual');
        await this.pyodide.runPythonAsync(this.code);
    }
}
"""


class MkPyodideTerminal(mknode.MkNode):
    """Node for embedding a Pyodide terminal running Python code."""

    ICON = "material/console"
    JS_FILES = [
        resources.JSFile(XTERM_JS, is_library=True),
        resources.JSFile(XTERM_FIT, is_library=True),
        resources.JSFile(PYODIDE_JS, is_library=True),
        resources.JSText(INIT_SCRIPT, "pyodide-terminal.js"),  # type: ignore[list-item]
    ]
    CSS = [resources.CSSFile(XTERM_CSS)]

    def __init__(
        self,
        code: str,
        *,
        height: str = "400px",
        width: str = "100%",
        terminal_id: str | None = None,
        **kwargs: Any,
    ):
        """Constructor.

        Args:
            code: Python code to run in the terminal
            height: Terminal height (CSS value)
            width: Terminal width (CSS value)
            terminal_id: Optional ID for the terminal element
            kwargs: Keyword arguments passed to parent
        """
        super().__init__(**kwargs)
        self.code = code
        self.height = height
        self.width = width
        self.terminal_id = terminal_id or f"pyodide-terminal-{id(self)}"

    def _to_markdown(self) -> str:
        """Convert the terminal to HTML."""
        html = f"""
        <div id="{self.terminal_id}" style="height: {self.height}; width: {self.width};"></div>
        <script>
        document.addEventListener('DOMContentLoaded', () => {{
            new PyodideTerminal(
                document.getElementById('{self.terminal_id}'),
                {self.code!r}
            );
        }});
        </script>
        """
        return "\n\n" + html + "\n\n"


if __name__ == "__main__":
    # Example usage in your documentation pages:
    terminal = MkPyodideTerminal("""
        from llmling_textual.creator import ConfigGeneratorApp
        app = ConfigGeneratorApp()
        app.run()
    """)
    print(terminal.to_markdown())
