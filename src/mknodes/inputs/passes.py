"""Render passes: rendering never fetches, missing inputs get resolved between passes.

The builder resolves the inputs nodes declare (`MkNode.get_input_requests()`) before
rendering. Some inputs only become known while rendering (nodes created by templates,
helpers like `iconcache.get_icon_svg`). Inside a render pass a read of a missing input
records it and raises `InputPendingError`; the render gets discarded (with the
diagnostics it reported), the recorded inputs get resolved (async, concurrently) and the
render runs again. With a complete lock file / store there is a single pass.
"""

from typing import TYPE_CHECKING

from mknodes.inputs.store import InputPendingError, RenderPass, current_pass, render_pass
from mknodes.utils import coroutines, diagnostics, log


if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable


logger = log.get_logger(__name__)

MAX_PASSES = 8
"""Passes before giving up (each pass may discover inputs needed by resolved ones)."""


class PendingInputsError(RuntimeError):
    """Inputs were still missing after `MAX_PASSES` render passes."""


def pending_error(render: RenderPass) -> PendingInputsError:
    """Return the error for inputs still missing after the last pass."""
    items = [f"{r.kind} {r.params}" for _, reqs in render.requests() for r in reqs]
    msg = f"Inputs still missing after {MAX_PASSES} render passes: {', '.join(items)}"
    return PendingInputsError(msg)


async def resolve_pending(render: RenderPass) -> None:
    """Resolve the inputs recorded by a render pass and drop the template render caches."""
    from mknodes.jinja import rendercache

    for store, requests in render.requests():
        logger.debug("Resolving %s inputs found while rendering", len(requests))
        await store.resolve(requests)
    # Templates rendered with a missing input must render again.
    rendercache.invalidate_all()


def run_passes[T](fn: Callable[[], T]) -> T:
    """Call `fn` (a render) in render passes until no input is missing (sync).

    Inside an active render pass `fn` just gets called: missing inputs go to the outer
    pass. Resolving runs `resolve_pending` in an event loop (a helper thread if one is
    running already), once per pass with missing inputs.
    """
    if current_pass() is not None:
        return fn()
    for _ in range(MAX_PASSES):
        with diagnostics.deferred() as held, render_pass() as render:
            try:
                result = fn()
            except Exception:
                if not render:
                    diagnostics.emit(held)
                    raise
        if not render:
            diagnostics.emit(held)
            return result
        coroutines.run_sync(resolve_pending(render))
    raise pending_error(render)


async def run_passes_async[T](fn: Callable[[], Awaitable[T]]) -> T:
    """Async version of `run_passes` (`fn` returns an awaitable render)."""
    if current_pass() is not None:
        return await fn()
    for _ in range(MAX_PASSES):
        with diagnostics.deferred() as held, render_pass() as render:
            try:
                result = await fn()
            except Exception:
                if not render:
                    diagnostics.emit(held)
                    raise
        if not render:
            diagnostics.emit(held)
            return result
        await resolve_pending(render)
    raise pending_error(render)


__all__ = [
    "MAX_PASSES",
    "InputPendingError",
    "PendingInputsError",
    "resolve_pending",
    "run_passes",
    "run_passes_async",
]
