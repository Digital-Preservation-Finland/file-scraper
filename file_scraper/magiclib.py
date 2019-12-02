"""Module to load proper magic module and file command paths.

   The module checks if the file command and magic library exists in the
   configuration paths, and will select these, if exist. If not, then
   system default file command and magic library is selected.
"""
from __future__ import print_function
import sys
import os.path
import ctypes
from file_scraper.shell import Shell
from file_scraper.utils import encode_path
from file_scraper.config import FILECMD_PATH, LD_LIBRARY_PATH, MAGIC_LIBRARY


def _is_file_path():
    """Checks if file command configuration paths exist.

    :returns: True, if configuration paths exist; False otherwise.
    """
    if os.path.isfile(FILECMD_PATH) and os.path.isdir(LD_LIBRARY_PATH):
        return True
    return False


def file_command(filename, parameters=None):
    """Uses file command in shell.

    :filename: Filename for the file command.
    :parameters: Parameter list for the file command.
    :returns: Shell class
    """
    cmd = "file"
    env = {}
    if _is_file_path():
        cmd = FILECMD_PATH
        env = {"LD_LIBRARY_PATH": LD_LIBRARY_PATH}

    if parameters is None:
        parameters = []
    return Shell([cmd] + parameters + [encode_path(filename)], env=env)


def magiclib():
    """Resolves magic library from the configuration path, and if missing,
    from the system path.

    :returns: magic library.
    """
    try:
        ctypes.cdll.LoadLibrary(MAGIC_LIBRARY)
    except OSError:
        print("%s not found, MS Office detection may not work properly if "
              "file command library is older." % MAGIC_LIBRARY,
              file=sys.stderr)
    try:
        import magic as magic
        return magic
    except ImportError:
        pass
    return None
