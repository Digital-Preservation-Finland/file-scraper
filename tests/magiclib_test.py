"""Tests for magiclib module
"""
import file_scraper.magiclib


def test_file_command():
    """Test that file command returns a mimetype
    """
    shell = file_scraper.magiclib.file_command(
        "tests/data/text_plain/valid__utf8_without_bom.txt",
        ["-be", "soft", "--mime-type"])
    assert 'text/plain' in shell.stdout
    assert shell.stderr == ""
    assert shell.returncode == 0


def test_analyze_magic():
    """Test that magic analysis function return a mimetype
    """
    magic_lib = file_scraper.magiclib.magiclib()
    mimetype = file_scraper.magiclib.magic_analyze(
        magic_lib, magic_lib.MAGIC_MIME_TYPE,
        "tests/data/text_plain/valid__utf8_without_bom.txt")
    assert mimetype == "text/plain"


def test_magiclib():
    """Test that magic library is found
    """
    magic_lib = file_scraper.magiclib.magiclib()
    assert magic_lib._libraries  # pylint: disable=protected-access
