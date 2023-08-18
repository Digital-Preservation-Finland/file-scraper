"""
Configuration settings of file-scraper.

The default values correspond to the installation paths used by the Finnish
national Digital Preservation Services. Installing the tools to other locations
is possible by editing the configuration file
'/etc/file-scraper/file-scraper.conf'. It is also possible to use another
configuration file by setting the environment variable 'FILE_SCRAPER_CONFIG'.
"""
import configparser
import os

DEFAULT_PATHS = {
                 "PSPP_PATH": "/usr/bin/pspp-convert",
                 "SCHEMATRON_DIRNAME": "/usr/share/iso_schematron_xslt1",
                 "VERAPDF_PATH": "/usr/share/java/verapdf/verapdf",
                 "VNU_PATH": "/usr/share/java/vnu/vnu.jar",
                 "SOFFICE_PATH": "/opt/libreoffice7.2/program/soffice"
                 }


def get_value(key):
    """Get a configuration value for a specific key."""
    return get_config_values()[key.upper()]


def get_config_values():
    """Get all the configuration keys and values."""
    paths = DEFAULT_PATHS
    config = read_config()
    if "PATHS" in config:
        for key, value in config["PATHS"].items():
            paths[key.upper()] = value
    return paths


def read_config():
    """Read a configuration file."""
    if hasattr(read_config, "_config_dict"):
        return read_config._config_dict
    config = configparser.ConfigParser()
    configfile_path = get_configfile_path()
    config.read(configfile_path)
    read_config._config_dict = config
    return read_config._config_dict


def get_configfile_path():
    """Get path to the configuration file."""
    configfile_path = os.getenv("FILE_SCRAPER_CONFIG",
                                "/etc/file-scraper/file-scraper.conf")
    return configfile_path


def config_filecmd_env():
    """
    Get path and environment for file command
    :returns: Path and environment for file command
    """
    filecmd_path = "/opt/file-5.30/bin/file"
    _magic_dir = "/opt/file-5.30/lib64/"
    if os.path.isfile(filecmd_path) and os.path.isfile(_magic_dir):
        return (filecmd_path, {"LD_LIBRARY_PATH": _magic_dir})

    if os.path.isfile(filecmd_path) and \
            os.path.isfile(_magic_dir.replace("lib64", "lib")):
        _magic_dir = _magic_dir.replace("lib64", "lib")
        return (filecmd_path, {"LD_LIBRARY_PATH": _magic_dir})

    return ("file", {})


def magic_library_path():
    """
    Get path for magic library
    :returns: Path for magic library
    """
    magic_file = "/opt/file-5.30/lib64/libmagic.so.1"
    if not os.path.isfile(magic_file) and \
            os.path.isfile(magic_file.replace("lib64", "lib")):
        return magic_file.replace("lib64", "lib")

    return magic_file
