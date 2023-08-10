from __future__ import annotations

from mkdocs import config


CONFIG = config.load_config("mkdocs.yml")


def get_repository_url():
    return CONFIG.repo_url


def get_site_url():
    return CONFIG.site_url


if __name__ == "__main__":
    url = get_repository_url()
    print(url)
