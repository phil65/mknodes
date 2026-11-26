"""External inputs (icons, licenses, LLM texts, git data, ...) resolved before rendering.

Nodes declare the inputs they need (`MkNode.get_input_requests`), the builder resolves
them concurrently before rendering, nodes read them from `ctx.inputs`. Locked kinds get
pinned in a lock file (`mknodes.lock`). Design + inventory: `design/inputs-store.md`.
"""

from mknodes.inputs.kinds import (
    KINDS,
    InputKind,
    InputUnavailableError,
    get_kind,
    register_kind,
)
from mknodes.inputs.store import (
    DEFAULT_LOCK_FILE,
    MODES,
    InputEntry,
    InputMode,
    InputPendingError,
    InputRequest,
    InputStore,
    MissingInputError,
    RenderPass,
    active_store,
    current_pass,
    default_store,
    get_input,
    render_pass,
    use_store,
)
from mknodes.inputs.passes import PendingInputsError, run_passes

__all__ = [
    "DEFAULT_LOCK_FILE",
    "KINDS",
    "MODES",
    "InputEntry",
    "InputKind",
    "InputMode",
    "InputPendingError",
    "InputRequest",
    "InputStore",
    "InputUnavailableError",
    "MissingInputError",
    "PendingInputsError",
    "RenderPass",
    "active_store",
    "current_pass",
    "default_store",
    "get_input",
    "get_kind",
    "register_kind",
    "render_pass",
    "run_passes",
    "use_store",
]
