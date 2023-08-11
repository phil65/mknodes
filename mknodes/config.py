from __future__ import annotations

from mkdocs import config


CONFIG = None

# Very dumb caching... Ideally we would be a proper plugin and get the config from
# the callbacks


def get_config():
    global CONFIG
    if CONFIG is None:
        CONFIG = config.load_config("mkdocs.yml")
    return CONFIG


def get_repository_url():
    return get_config().repo_url


def get_site_url():
    return get_config().site_url


def get_page_name():
    return get_config().site_name


def get_path(path: str) -> str:
    config = get_config()
    return path if config.use_directory_urls else f"{config.site_name}/{path}"


def get_inventory_info() -> list[dict]:
    """Returns list of dicts: [{"url": inventory_url, "domains": ["std", "py"]}, ...]."""
    config = get_config()
    try:
        return config.plugins["mkdocstrings"].config["handlers"]["python"]["import"]
    except KeyError:
        return []


if __name__ == "__main__":
    url = get_inventory_info()
    print(url)
