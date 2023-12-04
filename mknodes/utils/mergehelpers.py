from __future__ import annotations

from mknodes.utils import log


logger = log.get_logger(__name__)


def merge_extensions(dicts: list[dict[str, dict]]) -> list[dict[str, dict]]:
    seen = set()
    result = []
    dicts = [{k: dct[k]} for dct in dicts for k in dct]
    for dct in dicts:
        dct = dict(sorted(dct.items()))
        if (stringed := str(dct)) not in seen:
            seen.add(stringed)
            result.append(dct)
    return result
