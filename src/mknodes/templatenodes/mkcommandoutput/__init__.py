from typing import Any, TYPE_CHECKING

from mknodes import inputs
from mknodes.templatenodes import mktemplate
from mknodes.utils import log, resources

if TYPE_CHECKING:
    from collections.abc import Sequence


logger = log.get_logger(__name__)


class MkCommandOutput(mktemplate.MkTemplate):
    """Node to display the terminal output of a command."""

    ICON = "material/bash"
    STATUS = "new"
    CSS = [resources.CSSFile("terminal.css")]

    def __init__(self, call: Sequence[str], **kwargs: Any) -> None:
        """Constructor.

        Args:
            call: System call to make
            kwargs: Keyword arguments passed to parent
        """
        self.call = call
        super().__init__("output/html/template", **kwargs)

    @property
    def cwd(self):
        return self.ctx.metadata.repository_path

    def _command_params(self) -> dict[str, Any]:
        cwd = self.cwd
        return dict(call=" ".join(self.call), cwd=str(cwd) if cwd else None)

    def get_input_requests(self) -> list[inputs.InputRequest]:
        return [inputs.InputRequest.create("command", **self._command_params())]

    @property
    def output(self) -> str | None:
        """Output of the command (run in the resolve phase, inputs store kind `command`)."""
        return self.ctx.inputs.get("command", **self._command_params())


if __name__ == "__main__":
    text = MkCommandOutput.with_context(["dir"])
    print(text)
