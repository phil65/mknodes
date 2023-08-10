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


if __name__ == "__main__":
    url = get_repository_url()
    print(url)
