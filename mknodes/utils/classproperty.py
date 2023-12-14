from __future__ import annotations

from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from collections.abc import Callable


class ClassPropertyDescriptor:
    """A class property. Used for class attributes which should not resolve on loading.

    For an example, this can be used for class attributes which read from files, to
    avoid IO on loading.
    """

    def __init__(self, fget, fset=None):
        self.fget = fget
        self.fset = fset

    def __get__(self, obj: object, klass: type | None = None):
        if klass is None:
            klass = type(obj)
        return self.fget.__get__(obj, klass)()

    def __set__(self, obj: object, value):
        if not self.fset:
            msg = "can't set attribute"
            raise AttributeError(msg)
        type_ = type(obj)
        return self.fset.__get__(obj, type_)(value)

    def setter(self, func):
        if not isinstance(func, classmethod | staticmethod):
            func = classmethod(func)
        self.fset = func
        return self


def classproperty(func: Callable) -> ClassPropertyDescriptor:
    fn = func if isinstance(func, classmethod | staticmethod) else classmethod(func)
    return ClassPropertyDescriptor(fn)


if __name__ == "__main__":

    class Bar:
        _bar = 1

        @classproperty
        def bar(self):
            return self._bar

    print(Bar.bar)
    print(Bar().bar)
