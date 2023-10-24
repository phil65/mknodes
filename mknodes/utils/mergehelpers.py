from __future__ import annotations

from collections.abc import Mapping

from mknodes.utils import log


logger = log.get_logger(__name__)


STRATEGIES = {
    "additive": [
        (list, "append"),
        (dict, "merge"),
        (set, "union"),
    ],
    "replace": [
        (list, "override"),
        (dict, "override"),
        (set, "override"),
    ],
}


def merge_dicts(
    dct: Mapping,
    *dicts: Mapping,
    strategy: str = "additive",
    deepcopy: bool = False,
):
    import copy

    import deepmerge

    if deepcopy:
        dct = copy.deepcopy(dct)

    strat = STRATEGIES[strategy]
    merger = deepmerge.Merger(strat, ["override"], ["override"])
    for to_merge in dicts:
        dct = merger.merge(dct, to_merge)
    return dct


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


if __name__ == "__main__":
    dct_a = dict(a=[1, 2, 3], b={"test": "content"})
    dct_b = dict(a=[1, 2, 3], b={"test2": "content"})
    print(merge_dicts(dct_a, dct_b, strategy="additive"))
