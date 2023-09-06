from __future__ import annotations

from collections.abc import Mapping
import functools
import importlib

from importlib import metadata
import logging
import types

import pip._internal as pip


logger = logging.getLogger(__name__)


def install(package: str):
    pip.main(["install", package])


def install_or_import(package: str) -> types.ModuleType:
    try:
        return importlib.import_module(package)
    except ImportError:
        install(package)
        return importlib.import_module(package)


@functools.cache
def get_distribution(name: str) -> metadata.Distribution:
    return metadata.distribution(name)


@functools.cache
def get_metadata(dist: metadata.Distribution):
    return dist.metadata


@functools.cache
def get_requires(dist: metadata.Distribution) -> list[str]:
    return dist.requires or []


@functools.cache
def get_package_map() -> Mapping[str, list[str]]:
    return metadata.packages_distributions()


def distribution_to_package(dist):
    return next((k for k, v in get_package_map().items() if dist in v), dist)
