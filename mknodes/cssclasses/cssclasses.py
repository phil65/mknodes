from __future__ import annotations

from abc import ABCMeta
from collections.abc import MutableMapping

import cssutils


class StyleRule(MutableMapping, metaclass=ABCMeta):
    def __init__(self, rule: cssutils.css.CSSRule | str):
        if isinstance(rule, str):
            parser = cssutils.CSSParser(validate=False)
            stylesheet = parser.parseString(rule)
            rule = stylesheet.cssRules[0]
        self.rule = rule

    def __str__(self):
        return self.rule.cssText or ""

    def __getitem__(self, index: str) -> str:
        return self.rule.style[index]

    def __setitem__(self, index: str, value: str | tuple[str, str] | float):
        self.rule.style[index] = str(value) if isinstance(value, int | float) else value

    def set_value(self, index, value: str | float, important: bool = False):
        self.rule.style[index] = (str(value), "important") if important else str(value)

    def __delitem__(self, index: str):
        del self.rule.style[index]

    def __iter__(self):
        return iter(stylerule.name for stylerule in self.rule.style)

    def __len__(self):
        return len(self.rule.style)

    def __bool__(self):
        return bool(str(self).strip())

    @property
    def selector(self):
        return self.rule.selectorText if hasattr(self.rule, "selectorText") else None

    @classmethod
    def from_dict(cls, selector: str, data: dict):
        rule = cls(f"{selector}{{}}")
        for k, v in data.items():
            rule[k] = v
        return rule


class CSS:
    def __init__(self, text: str):
        parser = cssutils.CSSParser(validate=False)
        self.stylesheet = parser.parseString(text)
        self.rules = [StyleRule(rule) for rule in self.stylesheet.cssRules]

    def __getitem__(self, value: int | str):
        if isinstance(value, str):
            return next(rule for rule in self.rules if rule.selector == value)
        return self.rules[value]

    def __str__(self):
        return "\n".join(str(rule) for rule in self.rules)

    def __bool__(self):
        return bool(str(self).strip())

    def add_rule(self, selector: str, data: dict):
        rule = StyleRule.from_dict(selector, data)
        self.stylesheet.add(rule.rule)
        self.rules.append(rule)

    @classmethod
    def wrap_svg(cls, data: str):
        return f"url('data:image/svg+xml;charset=utf-8,{data}')"


if __name__ == "__main__":
    ss = CSS("")
    ss.add_rule("test", dict(a="b"))
    print(ss)
