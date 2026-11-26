"""External inputs (icons, licenses, LLM texts, git data, ...) resolved before rendering.

Nodes declare the inputs they need (`MkNode.get_input_requests`), the builder resolves
them concurrently before rendering, nodes read them from `ctx.inputs`. Locked kinds get
pinned in a lock file (`mknodes.lock`). Design + inventory: `design/inputs-store.md`.
"""

from __future__ import annotations

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
    InputRequest,
    InputStore,
    MissingInputError,
    active_store,
    use_store,
)

__all__ = [
    "DEFAULT_LOCK_FILE",
    "KINDS",
    "MODES",
    "InputEntry",
    "InputKind",
    "InputMode",
    "InputRequest",
    "InputStore",
    "InputUnavailableError",
    "MissingInputError",
    "active_store",
    "get_kind",
    "register_kind",
    "use_store",
]
