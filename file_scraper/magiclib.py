"""Module to load proper magic module and file command paths.

The module checks if the file command and magic library exists in the
configuration paths, and will select these, if exist. If not, then
system default file command is selected.
"""
from __future__ import annotations

import ctypes
from typing import TYPE_CHECKING

from file_scraper.paths import resolve_path_from_config

if TYPE_CHECKING:
    from pathlib import Path

    import magic


def magic_analyze(
    magic_lib: type[magic],
    magic_type: int,
    path: str | Path,
    magic_params: dict[int, int] | None = None,
) -> str | None:
    """Analyze file with given magic module.

    :param magic_lib: Magic module
    :param magic_type: Magic type to open magic library
    :param path: File path to analyze
    :param magic_params: Optional libmagic paramater overrides. See
        `MAGIC_PARAM_*_MAX` constants in the magic module for parameter IDs.
    :returns: Result from the magic module
    """
    magic_ = magic_lib.open(magic_type)
    if magic_ is None:
        return None

    magic_params = magic_params or {}

    try:
        magic_.load()

        for name, value in magic_params.items():
            success = magic_.setparam(name, min(2**31 - 1, value))
            if success == -1:
                raise ValueError(f"Invalid parameter: {name}")

        return magic_.file(path)
    finally:
        magic_.close()


def magiclib() -> type[magic]:
    """Resolve magic library from the configuration path.

    :returns: Magic module
    """
    try:
        ctypes.cdll.LoadLibrary(resolve_path_from_config("magiclib"))
    except OSError:
        pass

    # pylint: disable=import-outside-toplevel
    import magic
    return magic


def magiclib_version() -> str:
    """
    Define missing version function for the magic library
    :returns: magiclib version
    """
    magic_lib = magiclib()
    magic_version = magic_lib._libraries['magic'].magic_version
    magic_version.restype = ctypes.c_int
    magic_version.argtypes = []
    version_string = str(magic_version())
    return f"{version_string[0]}.{version_string[1:]}"
