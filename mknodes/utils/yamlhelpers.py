from __future__ import annotations

import pathlib

from typing import Any

import yaml

from mknodes.utils import log, mergehelpers


logger = log.get_logger(__name__)
YAMLError = yaml.YAMLError


def load_yaml_file(source, mode="unsafe", resolve_inherit: bool = True):
    path = pathlib.Path(source)
    text = path.read_text()
    result = load_yaml(text, mode=mode)
    if "INHERIT" in result and resolve_inherit:
        relpath = result.pop("INHERIT")
        abspath = path.absolute()
        if not abspath.exists():
            msg = f"Inherited config file '{relpath}' does not exist at '{abspath}'."
            raise FileNotFoundError(msg)
        logger.debug("Loading inherited configuration file: %s", abspath)
        parent_cfg = abspath.parent / relpath
        with parent_cfg.open("rb") as fd:
            text = fd.read().decode()
            parent = load_yaml(text, mode)
        # print(parent, result)
        result = mergehelpers.merge_dicts(parent, result)
    return result


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
            base_loader_cls: type = yaml.UnsafeLoader
        case "full":
            base_loader_cls = yaml.FullLoader
        case _:
            base_loader_cls = yaml.SafeLoader

    # Derive from global loader to leave the global loader unaltered.
    default_loader = get_default_loader(base_loader_cls)
    return yaml.load(text, Loader=default_loader)


def dump_yaml(yaml_obj: Any) -> str:
    return yaml.dump(yaml_obj, Dumper=yaml.Dumper, indent=2)


if __name__ == "__main__":
    cfg = load_yaml_file("mkdocs_generic.yml")
    print(cfg)
