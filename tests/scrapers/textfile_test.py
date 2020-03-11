"""
Test TextfileScraper, which determines whether file is a text file or not.

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
"""
from __future__ import unicode_literals

import pytest

from file_scraper.textfile.textfile_scraper import (TextfileScraper,
                                                    TextEncodingScraper)
from tests.common import parse_results, partial_message_included

VALID_MSG = "is a text file"
INVALID_MSG = "is not a text file"


@pytest.mark.parametrize(
    ["filename", "mimetype", "is_textfile"],
    [
        ("valid__utf8_without_bom.txt", "text/plain", True),
        ("valid__utf16le_bom.txt", "text/plain", True),
        ("valid__iso8859.txt", "text/plain", True),
        ("valid__utf16be_without_bom.txt", "text/plain", False),
        ("valid__utf32le_bom.txt", "text/plain", False),
        ("valid_1.0_well_formed.xml", "text/xml", True),
        ("valid_4.01.html", "text/html", True),
        ("invalid_4.01_illegal_tags.html", "text/html", True),
        ("valid_1.4.pdf", "application/pdf", False),
        ("valid_1987a.gif", "image/gif", False),
        ("invalid_1987a_broken_header.gif", "image/gif", False),
        ("invalid__empty.txt", "text/plain", False)
    ]
)
def test_existing_files(filename, mimetype, is_textfile, evaluate_scraper):
    """
    Test detecting whether file is a textfile.
    The scraper tool is not able to detect UTF-16 files without BOM nor
    UTF-32 files.

    :filename: Test file name
    :mimetype: File MIME type
    :is_textfile: Expected result whether a file is a text file or not
    """
    correct = parse_results(filename, mimetype, {}, True)
    scraper = TextfileScraper(filename=correct.filename,
                              mimetype="text/plain")
    scraper.scrape_file()

    if is_textfile:
        correct.streams[0]["stream_type"] = "text"
        correct.update_mimetype("text/plain")
        correct.streams[0]["version"] = "(:unap)"
    else:
        correct.streams[0]["stream_type"] = "(:unav)"
        correct.update_mimetype("(:unav)")
        correct.streams[0]["version"] = "(:unav)"

    correct.well_formed = is_textfile
    if correct.well_formed:
        correct.stdout_part = VALID_MSG
        correct.stderr_part = ""
        evaluate_scraper(scraper, correct)
    else:
        assert partial_message_included(INVALID_MSG, scraper.errors())
        assert scraper.errors()
        assert not scraper.well_formed


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
    ]
)
def test_encoding_check(filename, charset, is_wellformed, evaluate_scraper):
    """
    Test character encoding validation with brute force.

    :filename: Test file name
    :charset: Character encoding
    :is_wellformed: Expected result of well-formedness
    """
    params = {"charset": charset}
    correct = parse_results(filename, "text/plain", {}, True, params)
    scraper = TextEncodingScraper(filename=correct.filename,
                                  mimetype="text/plain", params=params)
    scraper.scrape_file()
    if not is_wellformed:
        correct.update_mimetype("(:unav)")
        correct.update_version("(:unav)")
    correct.well_formed = is_wellformed
    if correct.well_formed:
        correct.stdout_part = "encoding validated successfully"
        correct.stderr_part = ""
        evaluate_scraper(scraper, correct)
    else:
        assert partial_message_included("decoding error", scraper.errors())
        assert scraper.errors()
        assert not scraper.well_formed


@pytest.mark.parametrize(
    "charset",
    [
        ("(:unav)"), (None)
    ]
)
def test_encoding_not_defined(charset):
    """
    Test the case where encoding is not defined.

    :charset: Character encoding
    """
    scraper = TextEncodingScraper(
        filename="tests/data/text_plain/valid__utf8_without_bom.txt",
        mimetype="text/plain", params={"charset": charset})
    scraper.scrape_file()
    assert partial_message_included(
        "Character encoding not defined.", scraper.errors())


def test_decoding_limit(monkeypatch):
    """
    Test limiting the decoding.
    """
    monkeypatch.setattr(TextEncodingScraper, "_chunksize", 4)
    monkeypatch.setattr(TextEncodingScraper, "_limit", 8)
    scraper = TextEncodingScraper(
        filename="tests/data/text_plain/valid__utf8_bom.txt",
        mimetype="text/plain", params={"charset": "UTF-8"})
    scraper.scrape_file()
    assert partial_message_included(
        "First 8 bytes read, we skip the remainder", scraper.messages())
