"""Utilities for working with coroutines."""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, Any


if TYPE_CHECKING:
    from collections.abc import Coroutine


def run_sync[T](coro: Coroutine[Any, Any, T]) -> T:
    """Run a coroutine synchronously, handling nested event loops."""
    try:
        _loop = asyncio.get_running_loop()
    except RuntimeError:
        # No event loop running, safe to use asyncio.run
        return asyncio.run(coro)
    else:
        # Already in an event loop - need nest_asyncio or similar
        # For now, try to create a new loop in a thread
        import concurrent.futures

        with concurrent.futures.ThreadPoolExecutor() as pool:
            future = pool.submit(asyncio.run, coro)
            return future.result()
