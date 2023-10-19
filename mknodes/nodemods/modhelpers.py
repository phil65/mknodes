from __future__ import annotations


def format_js_map(dct: dict) -> str:
    """Return JS map str for given dictionary.

    Arguments:
        dct: Dictionary to dump
    """
    rows = []
    for k, v in dct.items():
        match v:
            case bool():
                rows.append(f"    {k}: {str(v).lower()},")
            case dict():
                rows.append(f"    {k}: {format_js_map(v)},")
            case None:
                rows.append(f"    {k}: null,")
            case _:
                rows.append(f"    {k}: {v!r},")
    row_str = "\n" + "\n".join(rows) + "\n"
    return f"{{{row_str}}}"


if __name__ == "__main__":
    dct = {
        "orientation": "right",
        "scale": 1.5,
        "overflow": True,
        "delay": 0.6,
        "transition": "cubic-bezier(0,0,0,1)",
        "maxTransition": 60,
    }
    result = format_js_map(dct)
    print(result)
