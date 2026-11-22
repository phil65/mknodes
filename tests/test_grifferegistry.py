from __future__ import annotations

from collections.abc import Mapping, MutableMapping

import pytest

from mknodes.info import grifferegistry


@pytest.mark.parametrize("klass", [MutableMapping, Mapping, "collections.abc.MutableMapping"])
def test_get_class_for_reexported_stdlib_classes(klass):
    result = grifferegistry.get_class(klass)
    assert result.name == (klass if isinstance(klass, str) else klass.__name__).rsplit(".")[-1]


def test_get_class_unknown_still_raises():
    with pytest.raises(KeyError):
        grifferegistry.get_class("collections.abc.DoesNotExist")
