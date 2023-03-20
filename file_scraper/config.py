"""
This file contains a centralized collection of configuration settings.

The default values correspond to the installation paths used by the Finnish
national Digital Preservation Services, but installing the tools to other
locations is possible by editing this file.
"""
import os.path

PSPP_PATH = "/usr/bin/pspp-convert"
SCHEMATRON_DIRNAME = "/usr/share/iso_schematron_xslt1"
VERAPDF_PATH = "/usr/share/java/verapdf/verapdf"
VNU_PATH = "/usr/share/java/vnu/vnu.jar"
SOFFICE_PATH = "/opt/libreoffice7.2/program/soffice"


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
