"""
Tests for magiclib module. This module tests that:
    - shell file command returns a mimetype
    - magic analysis function results a mimetype
    - magic library is found.
"""
import file_scraper.magiclib
from file_scraper.shell import Shell


def test_file_command():
    """Test that file command returns a mimetype"""
    shell = Shell(["file", "-be", "soft", "--mime-type",
                   "tests/data/text_plain/valid__utf8_without_bom.txt"])

    assert 'text/plain' in shell.stdout
    assert shell.stderr == ""
    assert shell.returncode == 0


def test_analyze_magic():
    """Test that magic analysis function return a mimetype"""
    magic_lib = file_scraper.magiclib.magiclib()
    mimetype = file_scraper.magiclib.magic_analyze(
        magic_lib, magic_lib.MAGIC_MIME_TYPE,
        "tests/data/text_plain/valid__utf8_without_bom.txt")
    assert mimetype == "text/plain"


def test_magiclib():
    """Test that magic library is found"""
    magic_lib = file_scraper.magiclib.magiclib()
    assert magic_lib._libraries  # pylint: disable=protected-access


def test_magiclib_version():
    """
    Test that magic_version follows strict X.YY format
    defined in the original header file for MAGIC_VERSION at
    https://github.com/file/file/blob/master/src/magic.h.in
    """
    magic_lib = file_scraper.magiclib
    version = magic_lib.magiclib_version()
    assert (version[0].isdigit() &
           (version[1] == '.') &
           version[2:].isnumeric())
    assert len(version) == 4
