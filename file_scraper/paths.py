"""
Path configuration of file-scraper.

Configuration:
    The paths used by national Digital Preservation Services are located inside
    the configuration file in: '/etc/file-scraper/file-scraper.conf'

    It is also possible to use another configuration file by setting the
    environment variable 'FILE_SCRAPER_CONFIG'. (when using another
    configuration file the config_names inside SOFTWARE_LOCATIONS cannot be
    trusted to be correct)

Priority:
    Path values resolved from the configuration file are prioritized over
    system path values found by the shutil library
"""
from __future__ import annotations

import configparser
import os
from pathlib import Path
import shutil


def get_config_path() -> str:
    """:returns: configuration environment variable"""
    return os.getenv("FILE_SCRAPER_CONFIG",
                     "/etc/file-scraper/file-scraper.conf")


def _find_from_config(
    section: str, config_name: str | bytes | Path
) -> str | None:
    """
    Attempts to find the given configuration name from the config file at
    the given section.

    :param section: section of configuration file to search
    :param config_name: configuration name to search

    :returns: value from the configuration or None
    """
    config_parser = configparser.ConfigParser()

    config_parser.read(get_config_path())
    if config_parser.has_section(section):
        config_section = config_parser[section]
        return config_section.get(str(config_name))
    return None


def resolve_command(command: str | bytes | Path) -> str:
    """
    Resolve section "COMMAND" from the configuration file,
    otherwise uses shutil.which function to determine the path of
    the executable.

    :param command: command string to resolve
    :returns: path specified by the configuration file or the path of the
        executable.
    :raises NameError: if the command cannot be found.
    """
    path_found = _find_from_config("COMMANDS", command)

    # Try to find the configuration value from the path.
    if path_found is None:
        path_found = shutil.which(command)

    # Raise and error if the value cannot be found.
    if path_found is None:
        raise FileNotFoundError(
            f"Configuration path: {command} "
            f"cannot be found from {get_config_path()} "
            f"or from the path: {os.environ.get('PATH', '')}")
    return str(path_found)


def resolve_path_from_config(config_name: str) -> str:
    """
    Resolves section "PATHS" from the configuration file.

    :param config_name: the config name to be searched.
    """
    path_found = _find_from_config("PATHS", config_name)
    if path_found is None:
        raise NameError(f"Configuration path: {config_name} "
                        f"cannot be found from the {get_config_path()}")
    return path_found
