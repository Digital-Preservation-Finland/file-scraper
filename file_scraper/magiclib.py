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


def file_command(filename, parameters=None):
    """Use file command in shell.

    :filename: Filename for the file command.
    :parameters: Parameter list for the file command.
    :returns: Shell class
    """
    cmd = "file"
    env = {}
    if os.path.isfile(FILECMD_PATH) and os.path.isdir(LD_LIBRARY_PATH):
        cmd = FILECMD_PATH
        env = {"LD_LIBRARY_PATH": LD_LIBRARY_PATH}
    elif os.path.isfile(FILECMD_PATH.replace("lib64", "lib")) and \
            os.path.isdir(LD_LIBRARY_PATH.replace("lib64", "lib")):
        cmd = FILECMD_PATH.replace("lib64", "lib")
        env = {"LD_LIBRARY_PATH": LD_LIBRARY_PATH.replace("lib64", "lib")}

    if parameters is None:
        parameters = []
    return Shell([cmd] + parameters + [encode_path(filename)], env=env)


def magic_analyze(magic_lib, magic_type, path):
    """Analyze file with given magic module.

    :magic_lib: Magic module
    :magic_type: Magic type to open magic library
    :path: File path to analyze
    :returns: Result from the magic module
    """
    magic_ = magic_lib.open(magic_type)
    magic_.load()
    magic_result = magic_.file(encode_path(path))
    magic_.close()
    return magic_result


def magiclib():
    """Resolve magic library from the configuration path, and if missing,
    from the system path.

    :returns: Magic module
    """
    try:
        if os.path.isfile(MAGIC_LIBRARY):
            ctypes.cdll.LoadLibrary(MAGIC_LIBRARY)
        else:
            ctypes.cdll.LoadLibrary(MAGIC_LIBRARY.replace("lib64", "lib"))
    except OSError:
        print("%s not found, MS Office detection may not work properly if "
              "file command library is older." % MAGIC_LIBRARY,
              file=sys.stderr)

    try:
        # pylint: disable=import-outside-toplevel
        import magic
        return magic
    except ImportError:
        pass
    return None
