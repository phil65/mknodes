from __future__ import annotations

from typing import TYPE_CHECKING, Any

import yamling

from mknodes.info import configfile
from mknodes.utils import log


if TYPE_CHECKING:
    import os


logger = log.get_logger(__name__)


class YamlFile(configfile.ConfigFile):
    filetype = "yaml"

    def load_file(
        self,
        path: str | os.PathLike[str],
        **storage_options: Any,
    ):
        """Load a file with loader of given file type.

        Args:
            path: Path to the config file (also supports fsspec protocol URLs)
            storage_options: Options for fsspec backend
        """
        self._data = yamling.load_yaml_file(
            path,
            storage_options=storage_options or {},
            resolve_inherit=True,
        )
        # type: ignore[arg-type]


if __name__ == "__main__":
    info = YamlFile(".pre-commit-config.yaml")
    print(info._data)
