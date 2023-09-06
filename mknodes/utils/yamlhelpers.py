from __future__ import annotations

import logging
import pathlib

import mergedeep
import yaml


logger = logging.getLogger(__name__)
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
        result = mergedeep.merge(parent, result)
    return result


def load_yaml(text: str, mode="unsafe"):
    import yaml_env_tag

    """Wrap PyYaml's loader so we can extend it to suit our needs."""
    match mode:
        case "unsafe":
            base_loader_cls: type = yaml.UnsafeLoader
        case "full":
            base_loader_cls = yaml.FullLoader
        case _:
            base_loader_cls = yaml.SafeLoader

    class MyLoader(base_loader_cls):
        """Derive from global loader to leave the global loader unaltered."""

    # Attach Environment Variable constructor.
    # See https://github.com/waylan/pyyaml-env-tag

    MyLoader.add_constructor("!ENV", yaml_env_tag.construct_env_tag)
    # if config is not None:
    #     MyLoader.add_constructor(
    #         "!relative", functools.partial(_construct_dir_placeholder, config)
    #     )
    return yaml.load(text, Loader=MyLoader)


def dump_yaml(yaml_obj) -> str:
    return yaml.dump(yaml_obj, Dumper=yaml.Dumper, indent=2)


if __name__ == "__main__":
    cfg = load_yaml_file("mkdocs_generic.yml")
    print(cfg)
