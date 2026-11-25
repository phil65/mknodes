"""The core (nodes, rendering, build) must not depend on the site generator."""

from __future__ import annotations

import subprocess
import sys


CORE_MODULES = ["mknodes", "mknodes.rendering", "mknodes.rendering.github", "mknodes.build"]


def test_core_does_not_import_site_generator():
    code = (
        "import sys\n"
        + "".join(f"import {mod}\n" for mod in CORE_MODULES)
        + "print(sorted(m for m in sys.modules if m.startswith(('mknodes.site', 'mknodes.cli'))))"
    )
    result = subprocess.run(
        [sys.executable, "-c", code], capture_output=True, text=True, check=True
    )
    assert result.stdout.strip() == "[]"
