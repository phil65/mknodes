from __future__ import annotations

import collections
import contextlib

from typing import Any

import yaml

from mknodes.utils import log


logger = log.get_logger(__name__)
YAMLError = yaml.YAMLError


def patch_dumper_to_not_order(dumper_cls):
    def map_representer(dumper_cls_, data):
        return dumper_cls_.represent_dict(data.items())

    yaml.add_representer(dict, map_representer, Dumper=dumper_cls)
    yaml.add_representer(collections.OrderedDict, map_representer, Dumper=dumper_cls)


def patch_pyyaml_to_not_order_dicts():
    _dumpers = [getattr(yaml.dumper, x) for x in yaml.dumper.__all__]
    with contextlib.suppress(AttributeError):
        _cyaml = yaml.cyaml.__all__
        _dumpers += [getattr(yaml.cyaml, x) for x in _cyaml if x.endswith("Dumper")]
    for dumper in _dumpers:
        patch_dumper_to_not_order(dumper)


# patch_pyyaml_to_not_order_dicts()


def get_safe_loader(base_loader_cls):
    class SafeLoader(base_loader_cls):
        """Safe Loader."""

    SafeLoader.add_constructor("!relative", lambda loader, node: None)  # type: ignore
    SafeLoader.add_multi_constructor(
        "tag:yaml.org,2002:python/name:",
        lambda loader, suffix, node: None,
    )
    SafeLoader.add_multi_constructor(
        "tag:yaml.org,2002:python/object/apply:",
        lambda loader, suffix, node: None,
    )
    return SafeLoader


def get_default_loader(base_loader_cls):
    # Attach Environment Variable constructor.
    # See https://github.com/waylan/pyyaml-env-tag

    import yaml_env_tag

    class DefaultLoader(base_loader_cls):
        """Default Loader."""

    DefaultLoader.add_constructor("!ENV", yaml_env_tag.construct_env_tag)
    # Loader.add_constructor("!ENV", lambda loader, node: None)  # type: ignore
    # if config is not None:
    #     Loader.add_constructor(
    #         "!relative", functools.partial(_construct_dir_placeholder, config)
    #     )
    return DefaultLoader


def load_yaml(text: str, mode="unsafe"):
    """Wrap PyYaml's loader so we can extend it to suit our needs."""
    match mode:
        case "unsafe":
            base_loader_cls: type = yaml.CUnsafeLoader
        case "full":
            base_loader_cls = yaml.CFullLoader
        case _:
            base_loader_cls = yaml.CSafeLoader

    # Derive from global loader to leave the global loader unaltered.
    default_loader = get_default_loader(base_loader_cls)
    return yaml.load(text, Loader=default_loader)


def dump_yaml(yaml_obj: Any) -> str:
    return yaml.dump(yaml_obj, Dumper=yaml.Dumper, indent=2)


if __name__ == "__main__":
    cfg = load_yaml("- test")
    print(cfg)
