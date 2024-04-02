"""Module to load proper magic module and file command paths.

   The module checks if the file command and magic library exists in the
   configuration paths, and will select these, if exist. If not, then
   system default file command is selected.
"""
import ctypes
from file_scraper.shell import Shell
from file_scraper.utils import encode_path
from file_scraper.config import config_filecmd_env, magic_library_path


def file_command(filename, parameters=None):
    """Use file command in shell.

    :filename: Filename for the file command.
    :parameters: Parameter list for the file command.
    :returns: Shell class
    """
    if parameters is None:
        parameters = []
    (filecmd_path, magic_env) = config_filecmd_env()
    return Shell([filecmd_path] + parameters + [encode_path(filename)],
                 env=magic_env)


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
    """Resolve magic library from the configuration path.

    :returns: Magic module
    """
    magic_file = magic_library_path()
    try:
        ctypes.cdll.LoadLibrary(magic_file)
    except OSError:
        pass

    try:
        # pylint: disable=import-outside-toplevel
        import magic
        return magic
    except ImportError:
        pass
    return None
