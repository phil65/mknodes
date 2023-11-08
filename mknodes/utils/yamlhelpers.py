from __future__ import annotations

import collections
import contextlib
import json
import os
import pathlib

from typing import Any, Literal

import yaml

from mknodes.utils import log


logger = log.get_logger(__name__)
YAMLError = yaml.YAMLError

LoaderStr = Literal["unsafe", "full", "safe"]


def _patch_dumper_to_not_order(dumper_cls):
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
        _patch_dumper_to_not_order(dumper)


# patch_pyyaml_to_not_order_dicts()


def yaml_include_constructor(loader: yaml.BaseLoader, node: yaml.Node) -> Any:
    """Include file referenced with !include node."""
    scalar = loader.construct_scalar(node)  # type: ignore[arg-type]
    folder = pathlib.Path(loader.name).parent
    fp = folder.joinpath(scalar).resolve()  # type: ignore[arg-type]
    fe = fp.suffix.lstrip(".")
    with fp.open() as f:
        if fe in ("yaml", "yml"):
            return yaml.load(f, type(loader))
        if fe in ("json", "jsn"):
            return json.load(f)
        return f.read()


def get_safe_loader(base_loader_cls: type):
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


def construct_env_tag(loader: yaml.Loader, node: yaml.Node) -> Any:
    """Assign value of ENV variable referenced at node."""
    default = None
    match node:
        case yaml.nodes.ScalarNode():
            variables = [loader.construct_scalar(node)]
        case yaml.nodes.SequenceNode():
            child_nodes = node.value
            if len(child_nodes) > 1:
                # default is resolved using YAML's (implicit) types.
                default = loader.construct_object(child_nodes[-1])
                child_nodes = child_nodes[:-1]
            # Env Vars are resolved as string values, ignoring (implicit) types.
            variables = [loader.construct_scalar(child) for child in child_nodes]
        case _:
            raise yaml.constructor.ConstructorError(
                None,
                None,
                f"expected a scalar or sequence node, but found {node.tag!r}",
                node.start_mark,
            )

    for var in variables:
        if var in os.environ:
            value = os.environ[str(var)]
            # Resolve value to Python type using YAML's implicit resolvers
            tag = loader.resolve(yaml.nodes.ScalarNode, value, (True, False))
            return loader.construct_object(yaml.nodes.ScalarNode(tag, value))

    return default


def get_default_loader(base_loader_cls: type):
    # Attach Environment Variable constructor.
    # See https://github.com/waylan/pyyaml-env-tag

    class DefaultLoader(base_loader_cls):
        """Default Loader."""

    DefaultLoader.add_constructor("!ENV", construct_env_tag)
    DefaultLoader.add_constructor("!include", yaml_include_constructor)
    # Loader.add_constructor("!ENV", lambda loader, node: None)  # type: ignore
    # if config is not None:
    #     Loader.add_constructor(
    #         "!relative", functools.partial(_construct_dir_placeholder, config)
    #     )
    return DefaultLoader


def load_yaml(text: str, mode: LoaderStr = "unsafe"):
    """Load a yaml string.

    Arguments:
        text: the string to load
        mode: the yaml loader mode.
    """
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
    """Dump a data structure to a yaml string.

    Arguments:
        yaml_obj: The object to serialize
    """
    return yaml.dump(yaml_obj, Dumper=yaml.Dumper, indent=2)


if __name__ == "__main__":
    cfg = load_yaml("- test")
    print(cfg)
