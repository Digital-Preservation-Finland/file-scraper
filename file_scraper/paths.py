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
import shutil


def get_config_path():
    """:returns: configuration environment variable"""
    return os.getenv("FILE_SCRAPER_CONFIG",
                     "/etc/file-scraper/file-scraper.conf")


def _find_from_config(section, config_name) -> str | None:
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
        section = config_parser[section]
        return section.get(config_name)


def resolve_command(command: str) -> str:
    """
    Resolve section "COMMAND" from the configuration file,
    otherwise uses shutil.which function to determine the path of
    the executable.

    :param command: command string to resolve

    :raises: NameError if the command cannot be found.

    :returns: path specified by the configuration file or the path of the
    executable.
    """

    path_found = _find_from_config("COMMANDS", command)

    # Try to find the configuration value from the path.
    if path_found is None:
        path_found = shutil.which(command)

    # Raise and error if the value cannot be found.
    if path_found is None:
        raise NameError(f"Configuration path: {command} cannot be found from"
                        f"{get_config_path()} or from the path: "
                        f"{os.environ.get('PATH', '')}")
    return path_found


def resolve_path_from_config(config_name):
    """
    Resolves section "PATHS" from the configuration file.

    :param config_name: the config name to be searched.
    """

    path_found = _find_from_config("PATHS", config_name)
    if path_found is None:
        raise NameError(f"Configuration path: {config_name} "
                        f"cannot be found from the {get_config_path()}")
    return path_found
