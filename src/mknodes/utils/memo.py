"""Memoize methods per instance, keyed on attributes of the instance."""

import functools
from typing import TYPE_CHECKING, Any


if TYPE_CHECKING:
    from collections.abc import Callable


def memoize_on[T](*attrs: str) -> Callable[[Callable[[Any], T]], Callable[[Any], T]]:
    """Cache the result of a no-argument method until one of given attributes changes.

    Used for children created by rendering a template: rendering is expensive and
    `get_children()` gets called many times per build (tree walks, `__bool__`, ...).

    Args:
        attrs: Instance attributes the result depends on
    """

    def decorator(method: Callable[[Any], T]) -> Callable[[Any], T]:
        slot = f"_memo_{method.__name__}"

        @functools.wraps(method)
        def wrapper(self: Any) -> T:
            key = tuple(getattr(self, attr) for attr in attrs)
            cached = self.__dict__.get(slot)
            if cached is not None and cached[0] == key:
                return cached[1]
            result = method(self)
            self.__dict__[slot] = (key, result)
            return result

        return wrapper

    return decorator
