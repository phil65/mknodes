from typing import Any

from mknodes.basenodes import mknode
from mknodes.utils import log, resources


logger = log.get_logger(__name__)

XTERM_CSS = "https://cdn.jsdelivr.net/npm/xterm/css/xterm.css"
XTERM_JS = "https://cdn.jsdelivr.net/npm/xterm/lib/xterm.js"
XTERM_FIT = "https://cdn.jsdelivr.net/npm/xterm-addon-fit/lib/xterm-addon-fit.js"
PYODIDE_VERSION = "314.0.8"


def pyodide_js_url(version: str = PYODIDE_VERSION) -> str:
    """Return the jsDelivr CDN URL for a given Pyodide version."""
    return f"https://cdn.jsdelivr.net/pyodide/v{version}/full/pyodide.js"


PYODIDE_JS = pyodide_js_url()

INIT_SCRIPT = """
class PyodideTerminal {
    constructor(element, code) {
        this.term = new Terminal({
            cols: 80,
            rows: 24,
            theme: { background: '#1a1a1a', foreground: '#ffffff' },
            cursorBlink: true
        });

        this.fitAddon = new FitAddon.FitAddon();
        this.term.loadAddon(this.fitAddon);
        this.term.open(element);
        this.fitAddon.fit();
        this.code = code;

        // Buffer to collect typed characters
        this.currentLine = '';

        this.term.onKey(({key, domEvent}) => {
            // Handle backspace
            if (domEvent.keyCode === 8) {
                if (this.currentLine.length > 0) {
                    this.currentLine = this.currentLine.slice(0, -1);
                    this.term.write('\b \b');
                }
            }
            // Handle enter/return
            else if (domEvent.keyCode === 13) {
                this.term.write('\\r\\n');
                this.executeCode(this.currentLine);
                this.currentLine = '';
            }
            // Handle regular keys
            else {
                const printable = !domEvent.altKey && !domEvent.altGraphKey &&
                                !domEvent.ctrlKey && !domEvent.metaKey;
                if (printable) {
                    this.currentLine += key;
                    this.term.write(key);
                }
            }
        });

        this.initPyodide();
    }

    async executeCode(code) {
        if (!code.trim()) return;
        try {
            const result = await this.pyodide.runPythonAsync(code);
            if (result !== undefined) {
                this.term.write('>>> ' + result + '\\r\\n');
            }
        } catch (error) {
            this.term.write('\\x1b[31m' + error + '\\x1b[0m\\r\\n');
        }
        this.term.write('>>> ');
    }

    async initPyodide() {
        this.pyodide = await loadPyodide({
            stdout: (text) => this.term.write(text),
            stderr: (text) => this.term.write(`\x1b[31m${text}\x1b[0m`)
        });

        await this.pyodide.loadPackage(['micropip']);
        await this.pyodide.runPythonAsync(this.code);
        this.term.write('>>> ');  // Initial prompt
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
        code: str = "",
        *,
        imports: list[str] | None = None,
        init_code: str | None = None,
        height: str = "400px",
        width: str = "100%",
        terminal_id: str | None = None,
        pyodide_version: str = PYODIDE_VERSION,
        **kwargs: Any,
    ) -> None:
        """Constructor.

        Args:
            code: Python code to show initially in terminal
            imports: List of packages to import during initialization
            init_code: Python code to execute during initialization
            height: Terminal height (CSS value)
            width: Terminal width (CSS value)
            terminal_id: Optional ID for the terminal element
            pyodide_version: Pyodide version to load from jsDelivr CDN
            kwargs: Keyword arguments passed to parent
        """
        super().__init__(**kwargs)
        self.code = code
        self.imports = imports or []
        self.init_code = init_code
        self.height = height
        self.width = width
        self.terminal_id = terminal_id or f"pyodide-terminal-{id(self)}"
        self.pyodide_version = pyodide_version

    def _build_node_resources(self) -> resources.Resources:
        res = super()._build_node_resources()
        if self.pyodide_version != PYODIDE_VERSION:
            target_url = pyodide_js_url(self.pyodide_version)
            res.js = [
                resources.JSFile(target_url, is_library=True)
                if isinstance(js, resources.JSFile) and js.link == PYODIDE_JS
                else js
                for js in res.js
            ]
        return res

    def to_md_unprocessed(self) -> str:
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
        import sys
        import micropip

        print(sys.version)
        await micropip.install("packaging")
    """)
    print(terminal.to_markdown_sync())
