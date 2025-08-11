"""
Test TextfileExtractor, which determines whether file is a text file or not.

This module tests that:
    - Following files are correctly identified as text files and their MIME
      type, version, streams and well-formedness are determined correctly:
        - plain text with either UTF-8 or Latin-1 encoding
        - xml document
        - html document
    - Empty file, pdf and gif files are identified as not text files.
    - Character encoding validation works as designed with all combinations of
      supported encodings.
    - Error message is given with missing character encoding
    - Limiting the decoding works as designed by reading the first 8 bytes
      and skipping the remainder
    - If a checked file contains illegal control characters, the actual
      characters are not printed in the error message, only their hex
      representation.
"""
from pathlib import Path

import pytest

from file_scraper.defaults import UNAP, UNAV
from file_scraper.shell import Shell
from file_scraper.textfile.textfile_extractor import (TextfileExtractor,
                                                      TextEncodingExtractor,
                                                      TextEncodingMetaExtractor)
from tests.common import parse_results, partial_message_included

VALID_MSG = "is a text file"
INVALID_MSG = "is not a text file"


def _new_file_version(version):
    """
    Check whether version of file command is given version or newer.
    """
    shell = Shell(["file", "--version"])
    ver = float(shell.stdout.split("\n")[0][len("file-"):])
    return True if ver >= version else False


@pytest.mark.parametrize(
    ["filename", "mimetype", "is_textfile", "special_handling"],
    [
        ("valid__utf8_without_bom.txt", "text/plain", True, False),
        ("valid__utf16le_bom.txt", "text/plain", True, False),
        ("valid__iso8859.txt", "text/plain", True, False),
        ("valid__utf16be_without_bom.txt", "text/plain", False, False),
        ("valid__utf32le_bom.txt", "text/plain", True, True),
        ("valid_1.0_well_formed.xml", "text/xml", True, False),
        ("valid_4.01.html", "text/html", True, False),
        ("invalid_4.01_illegal_tags.html", "text/html", True, False),
        ("valid_1.4.pdf", "application/pdf", False, False),
        ("valid_1987a.gif", "image/gif", False, False),
        ("invalid_1987a_broken_header.gif", "image/gif", False, False),
        ("invalid__empty.txt", "text/plain", False, False),
        ("invalid__unknown_encoding_cp437.txt", "text/plain", True, False),
    ]
)
def test_existing_files(filename, mimetype, is_textfile, special_handling,
                        evaluate_extractor):
    """
    Test detecting whether file is a textfile.
    The extractor tool is not able to detect UTF-16 files without BOM or
    UTF-32 files.

    :filename: Test file name
    :mimetype: File MIME type
    :is_textfile: Expected result whether a file is a text file or not
    :special_handling: True for UTF-32 encoded files, False for others
    """
    # UTF32 support for "file" command has existed since version 5.36.
    # With older version of "file" command, we can not handle UTF32 and
    # therefore valid__utf32le_bom.txt needs special handling.
    special_handling = special_handling and not _new_file_version(5.36)
    correct = parse_results(filename, mimetype, {}, False)
    extractor = TextfileExtractor(filename=correct.filename,
                                mimetype="text/plain")
    extractor.scrape_file()

    if is_textfile:
        correct.streams[0]["stream_type"] = "text"
        correct.update_mimetype("text/plain")
        correct.streams[0]["version"] = UNAP
    else:
        correct.streams[0]["stream_type"] = UNAV
        correct.update_mimetype(UNAV)
        correct.streams[0]["version"] = UNAV

    correct.well_formed = (False if special_handling or not is_textfile
                           else None)

    if correct.well_formed is False:
        assert partial_message_included(INVALID_MSG, extractor.errors())
        assert extractor.errors()
        assert extractor.well_formed is False
    elif correct.well_formed is None:
        correct.stdout_part = VALID_MSG
        correct.stderr_part = ""
        evaluate_extractor(extractor, correct)


@pytest.mark.parametrize(
    ["filename", "charset", "is_wellformed"],
    [
        ("valid__ascii.txt", "UTF-8", True),
        ("valid__ascii.txt", "UTF-16", False),
        ("valid__ascii.txt", "UTF-32", False),
        ("valid__ascii.txt", "ISO-8859-15", True),
        ("valid__utf8_without_bom.txt", "UTF-8", True),
        ("valid__utf8_without_bom.txt", "UTF-16", False),
        ("valid__utf8_without_bom.txt", "UTF-32", False),
        ("valid__utf8_without_bom.txt", "ISO-8859-15", False),
        ("valid__utf8_bom.txt", "UTF-8", True),
        ("valid__utf8_bom.txt", "UTF-16", False),
        ("valid__utf8_bom.txt", "UTF-32", False),
        ("valid__utf8_bom.txt", "ISO-8859-15", False),
        ("valid__utf16be_without_bom.txt", "UTF-8", False),
        ("valid__utf16be_without_bom.txt", "UTF-16", True),
        ("valid__utf16be_without_bom.txt", "UTF-32", False),
        ("valid__utf16be_without_bom.txt", "ISO-8859-15", False),
        ("valid__utf16be_bom.txt", "UTF-8", False),
        ("valid__utf16be_bom.txt", "UTF-16", True),
        ("valid__utf16be_bom.txt", "UTF-32", False),
        ("valid__utf16be_bom.txt", "ISO-8859-15", False),
        ("valid__utf16le_without_bom.txt", "UTF-8", False),
        ("valid__utf16le_without_bom.txt", "UTF-16", True),
        ("valid__utf16le_without_bom.txt", "UTF-32", False),
        ("valid__utf16le_without_bom.txt", "ISO-8859-15", False),
        ("valid__utf16le_bom.txt", "UTF-8", False),
        ("valid__utf16le_bom.txt", "UTF-16", True),
        ("valid__utf16le_bom.txt", "UTF-32", False),
        ("valid__utf16le_bom.txt", "ISO-8859-15", False),
        ("valid__utf32be_without_bom.txt", "UTF-8", False),
        ("valid__utf32be_without_bom.txt", "UTF-16", False),
        ("valid__utf32be_without_bom.txt", "UTF-32", True),
        ("valid__utf32be_without_bom.txt", "ISO-8859-15", False),
        ("valid__utf32be_bom.txt", "UTF-8", False),
        ("valid__utf32be_bom.txt", "UTF-16", False),
        ("valid__utf32be_bom.txt", "UTF-32", True),
        ("valid__utf32be_bom.txt", "ISO-8859-15", False),
        ("valid__utf32le_without_bom.txt", "UTF-8", False),
        ("valid__utf32le_without_bom.txt", "UTF-16", False),
        ("valid__utf32le_without_bom.txt", "UTF-32", True),
        ("valid__utf32le_without_bom.txt", "ISO-8859-15", False),
        ("valid__utf32le_bom.txt", "UTF-8", False),
        ("valid__utf32le_bom.txt", "UTF-16", False),
        ("valid__utf32le_bom.txt", "UTF-32", True),
        ("valid__utf32le_bom.txt", "ISO-8859-15", False),
        ("valid__iso8859.txt", "UTF-8", False),
        ("valid__iso8859.txt", "UTF-16", False),
        ("valid__iso8859.txt", "UTF-32", False),
        ("valid__iso8859.txt", "ISO-8859-15", True),
        ("invalid__empty.txt", "ISO-8859-15", True),
        ("valid__utf16le_multibyte.txt", "UTF-16", True),
        ("valid__utf16be_multibyte.txt", "UTF-16", True),
        ("valid__utf8_multibyte.txt", "UTF-8", True),
        ("invalid__utf8_just_c3.txt", "UTF-8", False),
        ("invalid__unknown_encoding_cp437.txt", "UNKNOWN-8BIT", False),
        ("invalid__unknown_encoding_cp437.txt", "ISO-8859-15", False),
    ]
)
def test_encoding_check(filename, charset, is_wellformed, evaluate_extractor):
    """
    Test character encoding validation with brute force.

    :filename: Test file name
    :charset: Character encoding
    :is_wellformed: Expected result of well-formedness
    """
    params = {"charset": charset}
    correct = parse_results(filename, "text/plain", {}, True, params)
    extractor = TextEncodingExtractor(filename=correct.filename,
                                    mimetype="text/plain", params=params)
    extractor.scrape_file()
    if not is_wellformed:
        correct.update_mimetype(UNAV)
        correct.update_version(UNAV)
        correct.streams[0]["stream_type"] = UNAV
    else:
        correct.update_mimetype("text/plain")
        correct.update_version(UNAP)
        correct.streams[0]["stream_type"] = "text"

    correct.well_formed = is_wellformed
    if correct.well_formed:
        correct.stdout_part = "encoding validated successfully"
        correct.stderr_part = ""
        evaluate_extractor(extractor, correct)
    else:
        assert partial_message_included("decoding error", extractor.errors())
        assert extractor.errors()
        assert not extractor.well_formed


@pytest.mark.parametrize(
    "charset",
    [
        (UNAV), (None)
    ]
)
def test_encoding_not_defined(charset):
    """
    Test the case where encoding is not defined.

    :charset: Character encoding
    """
    extractor = TextEncodingExtractor(
        filename=Path("tests/data/text_plain/valid__utf8_without_bom.txt"),
        mimetype="text/plain", params={"charset": charset})
    extractor.scrape_file()
    assert partial_message_included(
        "Character encoding not defined.", extractor.errors())


def test_decoding_limit(monkeypatch):
    """
    Test limiting the decoding.
    """
    monkeypatch.setattr(TextEncodingExtractor, "_chunksize", 4)
    monkeypatch.setattr(TextEncodingExtractor, "_limit", 8)
    extractor = TextEncodingExtractor(
        filename=Path("tests/data/text_plain/valid__utf8_bom.txt"),
        mimetype="text/plain", params={"charset": "UTF-8"})
    extractor.scrape_file()
    assert partial_message_included(
        "First 8 bytes read, we skip the remainder", extractor.messages())


def test_error_message_control_character():
    """
    Make sure that no actual illegal control characters are included
    in the extractor error message, only their hex representation.
    The error message may be printed into an XML file, and XML
    files do not allow most control characters.
    """
    extractor = TextEncodingExtractor(
        filename=Path("tests/data/text_plain/invalid__control_character.txt"),
        mimetype="text/plain", params={"charset": "UTF-8"})
    extractor.scrape_file()
    assert not partial_message_included("\x1f", extractor.errors())
    character = "'\\x1f'"
    assert partial_message_included(
            "Illegal character %s in position 4" % character, extractor.errors())


def test_tools():
    """
    Test that tools return correct software
    """
    text_extractor = TextfileExtractor(filename=Path(""), mimetype="")
    text_encoding_extractor = TextEncodingExtractor(filename=Path(""), mimetype="")
    text_meta_extractor = TextEncodingMetaExtractor(filename=Path(""), mimetype="")
    assert text_extractor.tools()["file"]["version"][0].isdigit()
    assert text_encoding_extractor.tools() == {}
    assert text_meta_extractor.tools() == {}
