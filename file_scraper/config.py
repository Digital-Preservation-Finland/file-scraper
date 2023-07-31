"""
TODO
"""
import os
import click
import configparser

DEFAULT_PATHS = {
                 "PSPP_PATH": "/usr/bin/pspp-convert",
                 "SCHEMATRON_DIRNAME": "/usr/share/iso_schematron_xslt1",
                 "VERAPDF_PATH": "/usr/share/java/verapdf/verapdf",
                 "VNU_PATH": "/usr/share/java/vnu/vnu.jar",
                 "SOFFICE_PATH": "/opt/libreoffice7.2/program/soffice"
                 }


def get_value(key, configfile=None):
    # check if user provided a configfile
    if configfile:
        config = read_config(configfile)
        return config["PATHS"][key]

    # check for a config file in the default path
    config_in_default = check_configfile_in_default_location()
    if config_in_default:
        config = read_config(config_in_default)
        return config["PATHS"][key]

    # return default values
    return DEFAULT_PATHS[key.upper()]


def get_default_configfile_path():
    return click.get_app_dir("file_scraper")


def read_config(configfile):
    if not os.path.isfile(configfile):
        raise FileNotFoundError("Invalid config file path")
    config = configparser.ConfigParser()
    config.read(configfile)
    return config


def check_configfile_in_default_location():
    conf_default_location = os.path.join(
                                get_default_configfile_path(),
                                "config.conf")
    if os.path.isfile(conf_default_location):
        return conf_default_location
    return None


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
