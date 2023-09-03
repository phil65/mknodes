from __future__ import annotations

import logging


logger = logging.getLogger(__name__)


def load_yaml(text: str, mode="unsafe"):
    import yaml
    import yaml_env_tag

    """Wrap PyYaml's loader so we can extend it to suit our needs."""
    match mode:
        case "unsafe":
            base_loader_cls: type = yaml.UnsafeLoader
        case "full":
            base_loader_cls = yaml.FullLoader
        case "safe":
            base_loader_cls = yaml.SafeLoader
        case _:
            base_loader_cls = yaml.Loader

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
    import yaml

    return yaml.dump(yaml_obj, Dumper=yaml.Dumper, indent=2)


if __name__ == "__main__":
    strings = dump_yaml([str(i) for i in range(1000)])
    print(strings)
