"""Smoke test: the package imports and reports its version."""

import mknodes


def test_package_imports() -> None:
    """The package can be imported and exposes a version string."""
    assert isinstance(mknodes.__version__, str)
