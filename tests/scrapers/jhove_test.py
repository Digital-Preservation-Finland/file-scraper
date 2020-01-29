"""
Test module for jhove.py

This module tests that:
    - MIME type, version, streams and well-formedness of gif 1987a and 1989a
      files is tested correctly.
        - For well-formed files, scraper messages contains "Well-Formed and
          valid".
        - For files with broken header, scraper errors contains "Invalid GIF
          header".
        - For truncated files, scraper errors contains "Unknown data block
          type".
        - For empty files, scraper errors contains "Invalid GIF header".
    - MIME type, version, streams and well-formedness of tiff files is tested
      correctly.
        - For well-formed files, scraper messages contains "Well-Formed and
          valid".
        - For files with altered payload, scraper messages contains "IDF offset
          not word-aligned".
        - For files with wrong byte order reported, scraper messages contains
          "No TIFF magic number".
        - For empty files, scraper errors contains "File is too short".
    - MIME type, version, streams and well-formedness of UTF-8 text files is
      tested correctly.
        - For files with UTF-8 and ASCII (backwards compatibility) encodings
          scraper messages contains "Well-Formed and valid".
        - For files with ISO-8859 encoding scraper errors contains "Not valid
          second byte of UTF-8 encoding"
    - MIME type, version, streams and well-formedness of pdf 1.2, 1.3, 1.4,
      1.5, 1.6 and A-1a files is tested correctly.
        - For valid files, scraper messages contains "Well-formed and valid".
        - For files with altered payload, scraper errors contains "Invalid
          object definition".
        - For files with removed xref entry, scraper errors contains
          "Improperly nested dictionary delimiters".
        - For files with wrong version in header, scraper errors contains
          "Version 1.0 is not supported."
    - MIME type, version, streams and well-formedness of jpeg 1.01 files is
      tested correctly
        - For valid files, scraper messages contains "Well-formed and valid".
        - For files with altered payload, scraper errors contains "Unexpected
          end of file".
        - For files without FF D8 FF start marker, scraper errors contains
          "Invalid JPEG header".
        - For empty files, scraper errors contains "Invalid JPEG header".
    - MIME type, version, streams and well-formedness of html 4.01 and
      xhtml 1.0 files is tested correctly
        - For valid files, scraper messages contains "Well-formed and valid".
        - For valid html file with version not supported by the scraper,
          scraper errors contains "Unrecognized or missing DOCTYPE
          declaration".
        - For html files with illegal tags, scraper errors contains "Unknown
          tag".
        - For html files without doctype, scraper errors contains
          "Unrecognized or missing DOCTYPE declaration".
        - For empty files, scraper errors contains "Document is empty".
        - For xhtml files with illegal tags, scraper errors contains "must be
          declared".
        - For xhtml files without doctype, scraper errors contains "Cannot
          find the declaration of element".
    - MIME type, version, streams and well-formedness of bwf and wav files is
      tested correctly
        - For valid files, scraper messages contains "Well-formed and valid".
        - For bwf files with missing bytes, scraper messages contains "Invalid
          character in Chunk ID".
        - For bwf and wav files with bytes removed from the RIFF tag, scraper
          errors contains "Invalid chunk size".
        - For empty files, scraper errors contains "Unexpected end of file".
        - For files with missing data bytes, scraper errors contains "Bytes
          missing".

    - When well-formedness is not checked, scraper errors contains "Skipping
      scraper" and well_formed is None for all scrapers.

    - The following MIME-type and version pairs are supported by their
      respective scrapers when well-formedness is checked, in addition to
      which these MIME types are also supported with None or a made up version.
      When well-formedness is not checked, these MIME types are not supported.
        - image/gif, 1989a
        - image/tiff, 6.0
        - image/jpeg, 1.01
        - audio/x-wav, 2
    - The following MIME type and version pairs are supported by their
      respective scrapers when well-formedness is checked. They are not
      supported with a made up version or when well-formedness is not checked.
        - application/pdf, 1.4
        - text/html, 4.01
        - application/xhtml+xml, 1.0
    - Utf8JHove reports MIME type text/plain with "", None or a made up version
      as not supported, as well as a made up MIME type.

    - Forcing MIME types and/or versions works.
"""
from __future__ import unicode_literals

import os

import pytest

from file_scraper.jhove.jhove_scraper import (JHoveGifScraper,
                                              JHoveHtmlScraper,
                                              JHoveJpegScraper,
                                              JHovePdfScraper,
                                              JHoveTiffScraper,
                                              JHoveUtf8Scraper,
                                              JHoveWavScraper)
from tests.common import (parse_results, force_correct_filetype,
                          partial_message_included)


@pytest.mark.parametrize(
    ["filename", "result_dict", "get_ver"],
    [
        ("valid_XXXXa.gif", {
            "purpose": "Test valid file.",
            "stdout_part": "Well-Formed and valid",
            "stderr_part": ""}, True),
        ("invalid_XXXXa_broken_header.gif", {
            "purpose": "Test invalid header.",
            "stdout_part": "",
            "stderr_part": "Invalid GIF header"}, False),
        ("invalid_XXXXa_truncated.gif", {
            "purpose": "Test truncated file.",
            "stdout_part": "",
            "stderr_part": "Unknown data block type"}, True),
        ("invalid__empty.gif", {
            "purpose": "Test empty file.",
            "stdout_part": "",
            "stderr_part": "Invalid GIF header"}, False)
    ]
)
def test_scraper_gif(filename, result_dict, get_ver, evaluate_scraper):
    """Test gif scraping."""
    for version in ["1987", "1989"]:
        filename = filename.replace("XXXX", version)
        correct = parse_results(filename, "image/gif",
                                result_dict, True)
        scraper = JHoveGifScraper(correct.filename, True, correct.params)
        scraper.scrape_file()
        if not get_ver:
            correct.version = None
            correct.streams[0]["version"] = "(:unav)"

        evaluate_scraper(scraper, correct)


@pytest.mark.parametrize(
    ["filename", "result_dict"],
    [
        ("valid_6.0.tif", {
            "purpose": "Test valid file.",
            "stdout_part": "Well-Formed and valid",
            "stderr_part": ""}),
        ("invalid_6.0_payload_altered.tif", {
            "purpose": "Test payload altered in file.",
            "stdout_part": "",
            "stderr_part": "IFD offset not word-aligned"}),
        ("invalid_6.0_wrong_byte_order.tif", {
            "purpose": "Test wrong byte order in file.",
            "stdout_part": "",
            "stderr_part": "No TIFF magic number"}),
        ("invalid__empty.tif", {
            "purpose": "Test empty file.",
            "stdout_part": "",
            "stderr_part": "File is too short"}),
    ]
)
def test_scraper_tiff(filename, result_dict, evaluate_scraper):
    """Test tiff scraping."""
    correct = parse_results(filename, "image/tiff",
                            result_dict, True)
    scraper = JHoveTiffScraper(correct.filename, True, correct.params)
    scraper.scrape_file()
    correct.version = "6.0"
    correct.streams[0]["version"] = "6.0"

    evaluate_scraper(scraper, correct)


@pytest.mark.parametrize(
    ["filename", "result_dict"],
    [
        ("valid__utf8_without_bom.txt", {
            "purpose": "Test valid UTF-8 file.",
            "stdout_part": "Well-Formed and valid",
            "stderr_part": ""}),
        ("valid__ascii.txt", {
            "purpose": "Test valid ASCII file.",
            "stdout_part": "Well-Formed and valid",
            "stderr_part": ""}),
        ("valid__iso8859.txt", {
            "purpose": "Test valid ISO-8859 file, which is invalid.",
            "inverse": True,
            "stdout_part": "",
            "stderr_part": "Not valid second byte of UTF-8 encoding"})
    ]
)
def test_scraper_utf8(filename, result_dict, evaluate_scraper):
    """Test utf8 text file scraping."""
    correct = parse_results(filename, "text/plain", result_dict, True,
                            {"charset": "UTF-8"})
    scraper = JHoveUtf8Scraper(correct.filename, True, correct.params)
    scraper.scrape_file()
    correct.mimetype = None
    correct.version = None
    correct.streams[0]["mimetype"] = "(:unav)"

    evaluate_scraper(scraper, correct)


@pytest.mark.parametrize(
    ["filename", "result_dict", "version"],
    [
        ("valid_X.pdf", {
            "purpose": "Test valid file.",
            "stdout_part": "Well-Formed and valid",
            "stderr_part": ""}, "X"),
        ("invalid_X_payload_altered.pdf", {
            "purpose": "Test payload altered file.",
            "stdout_part": "",
            "stderr_part": "Invalid object definition"}, None),
        ("invalid_X_removed_xref.pdf", {
            "purpose": "Test xref change.",
            "stdout_part": "",
            "stderr_part": "Improperly nested dictionary delimiters"}, None),
    ]
)
def test_scraper_pdf(filename, result_dict, version, evaluate_scraper):
    """Test pdf scraping."""
    for ver in ["1.2", "1.3", "1.4", "1.5", "1.6", "A-1a"]:
        filename = filename.replace("X", ver)
        correct = parse_results(filename, "application/pdf",
                                result_dict, True)
        scraper = JHovePdfScraper(correct.filename, True, correct.params)
        scraper.scrape_file()
        if version in [None, "1.0"]:
            correct.version = version
            correct.streams[0]["version"] = version

        evaluate_scraper(scraper, correct)


def test_scraper_invalid_pdfversion():
    """Test that wrong version is detected."""
    for ver in ["1.2", "1.3", "1.4", "1.5", "1.6", "A-1a"]:
        scraper = JHovePdfScraper("tests/data/application_pdf/"
                                  "invalid_X_wrong_version.pdf".replace("X",
                                                                        ver),
                                  True)
    scraper.scrape_file()
    assert partial_message_included(
        "MIME type application/pdf with version 1.0 is not supported.",
        scraper.errors())
    assert not scraper.well_formed


@pytest.mark.parametrize(
    ["filename", "result_dict"],
    [
        ("valid_1.01.jpg", {
            "purpose": "Test valid file.",
            "stdout_part": "Well-Formed and valid",
            "stderr_part": ""}),
        ("invalid_1.01_data_changed.jpg", {
            "purpose": "Test image data change in file.",
            "stdout_part": "",
            "stderr_part": "Unexpected end of file"}),
        ("invalid_1.01_no_start_marker.jpg", {
            "purpose": "Test start marker change in file.",
            "stdout_part": "",
            "stderr_part": "Invalid JPEG header"}),
        ("invalid__empty.jpg", {
            "purpose": "Test empty file.",
            "stdout_part": "",
            "stderr_part": "Invalid JPEG header"})
    ]
)
def test_scraper_jpeg(filename, result_dict, evaluate_scraper):
    """Test jpeg scraping."""
    correct = parse_results(filename, "image/jpeg",
                            result_dict, True)
    scraper = JHoveJpegScraper(correct.filename, True, correct.params)
    scraper.scrape_file()
    correct.version = "(:unav)"
    correct.streams[0]["version"] = "(:unav)"

    evaluate_scraper(scraper, correct)


# pylint: disable=too-many-arguments
@pytest.mark.parametrize(
    ["filename", "result_dict", "mimetype", "charset", "version"],
    [
        ("valid_4.01.html", {
            "purpose": "Test valid file with correctly specified charset.",
            "stdout_part": "Well-Formed and valid",
            "stderr_part": ""},
         "text/html", "UTF-8", "4.01"),
        ("valid_4.01.html", {
            "purpose": "Test valid file with incorrectly specified charset.",
            "stdout_part": "",
            "inverse": True,
            "stderr_part": "Found encoding declaration UTF-8"},
         "text/html", "ISO-8859-15", "4.01"),
        ("valid_1.0.xhtml", {
            "purpose": "Test valid file.",
            "stdout_part": "Well-Formed and valid",
            "stderr_part": ""},
         "application/xhtml+xml", "UTF-8", "1.0"),
        ("valid_5.0.html", {
            "purpose": "Test valid file, which is invalid for this scraper.",
            "inverse": True,
            "stdout_part": "",
            "stderr_part": "Unrecognized or missing DOCTYPE declaration"},
         "text/html", None, None),
        ("invalid_4.01_illegal_tags.html", {
            "purpose": "Test illegal tag.",
            "stdout_part": "",
            "stderr_part": "Unknown tag"},
         "text/html", None, "4.01"),
        ("invalid_4.01_nodoctype.html", {
            "purpose": "Test without doctype.",
            "stdout_part": "",
            "stderr_part": "Unrecognized or missing DOCTYPE declaration"},
         "text/html", None, None),
        ("invalid__empty.html", {
            "purpose": "Test empty file.",
            "stdout_part": "",
            "stderr_part": "Document is empty"},
         "text/html", None, None),
        ("invalid_1.0_illegal_tags.xhtml", {
            "purpose": "Test illegal tag.",
            "stdout_part": "",
            "stderr_part": "must be declared."},
         "application/xhtml+xml", "UTF-8", "1.0"),
        ("invalid_1.0_missing_closing_tag.xhtml", {
            "purpose": "Test missing closing tag.",
            "stdout_part": "",
            "stderr_part": "must be terminated by the matching end-tag"},
         "application/xhtml+xml", None, None),
        ("invalid_1.0_no_doctype.xhtml", {
            "purpose": "Test without doctype.",
            "stdout_part": "",
            "stderr_part": "Cannot find the declaration of element"},
         "application/xhtml+xml", "UTF-8", "1.0"),
        ("invalid__empty.xhtml", {
            "purpose": "Test empty file.",
            "stdout_part": "",
            "stderr_part": "Document is empty"},
         "application/xhtml+xml", None, None)
    ]
)
def test_scraper_html(filename, result_dict, mimetype, charset, version,
                      evaluate_scraper):
    """Test html and xhtml scraping."""
    params = {"charset": charset}
    correct = parse_results(filename, mimetype, result_dict, True,
                            params)
    scraper = JHoveHtmlScraper(correct.filename, True, correct.params)
    scraper.scrape_file()
    correct.streams[0]["stream_type"] = "text"
    correct.version = version
    correct.streams[0]["version"] = version
    if "invalid__empty.xhtml" in filename:
        correct.mimetype = "text/html"
        correct.streams[0]["mimetype"] = "text/html"

    evaluate_scraper(scraper, correct)
# pylint: enable=too-many-arguments


@pytest.mark.parametrize(
    ["filename", "result_dict", "version"],
    [
        ("valid__wav.wav", {
            "purpose": "Test valid file.",
            "stdout_part": "Well-Formed and valid",
            "stderr_part": ""},
         None),
        ("valid_2_bwf.wav", {
            "purpose": "Test valid file.",
            "stdout_part": "Well-Formed and valid",
            "stderr_part": ""},
         "2"),
        ("invalid_2_bwf_data_bytes_missing.wav", {
            "purpose": "Test data bytes missing.",
            "stdout_part": "",
            "stderr_part": "Invalid character in Chunk ID"},
         None),
        ("invalid_2_bwf_RIFF_edited.wav", {
            "purpose": "Test edited RIFF.",
            "stdout_part": "",
            "stderr_part": "Invalid chunk size"},
         None),
        ("invalid__data_bytes_missing.wav", {
            "purpose": "Test data bytes missing.",
            "stdout_part": "",
            "stderr_part": "Bytes missing"},
         None),
        ("invalid__RIFF_edited.wav", {
            "purpose": "Test edited RIFF.",
            "stdout_part": "",
            "stderr_part": "Invalid chunk size"},
         None)
    ]
)
def test_scraper_wav(filename, result_dict, version, evaluate_scraper):
    """Test wav and bwf scraping."""
    correct = parse_results(filename, "audio/x-wav",
                            result_dict, True)
    scraper = JHoveWavScraper(correct.filename, True, correct.params)
    scraper.scrape_file()
    if "empty" in filename:
        correct.mimetype = None
        correct.streams[0]["mimetype"] = None
    correct.version = version
    if "invalid" in filename or "2" not in filename:
        correct.streams[0]["version"] = "(:unav)"

    evaluate_scraper(scraper, correct)


@pytest.mark.parametrize(
    ["scraper_class", "filename", "mime"],
    [
        (JHoveGifScraper, "valid_1989a.gif", "image/gif"),
        (JHoveTiffScraper, "valid_6.0.tif", "image/tiff"),
        (JHovePdfScraper, "valid_1.4.pdf", "application/pdf"),
        (JHoveUtf8Scraper, "valid__utf8_without_bom.txt", "text/plain"),
        (JHoveJpegScraper, "valid_1.01.jpg", "image/jpeg"),
        (JHoveHtmlScraper, "valid_4.01.html", "text/html"),
        (JHoveWavScraper, "valid__wav.wav", "audio/x-wav")
    ]
)
def test_no_wellformed(scraper_class, filename, mime):
    """Test scrapers without well-formed check."""
    scraper = scraper_class(os.path.join("tests/data/",
                                         mime.replace("/", "_"),
                                         filename),
                            False)
    scraper.scrape_file()
    assert partial_message_included("Skipping scraper", scraper.messages())
    assert scraper.well_formed is None


@pytest.mark.parametrize(
    ["mime", "ver", "class_"],
    [
        ("image/gif", "1989a", JHoveGifScraper),
        ("image/tiff", "6.0", JHoveTiffScraper),
        ("image/jpeg", "1.01", JHoveJpegScraper),
        ("audio/x-wav", "2", JHoveWavScraper)
    ]
)
def test_is_supported_allow(mime, ver, class_):
    """Test is_supported method, allow all versions."""
    assert class_.is_supported(mime, ver, True)
    assert class_.is_supported(mime, None, True)
    assert not class_.is_supported(mime, ver, False)
    assert class_.is_supported(mime, "foo", True)
    assert not class_.is_supported("foo", ver, True)


@pytest.mark.parametrize(
    ["mime", "ver", "class_"],
    [
        ("application/pdf", "1.4", JHovePdfScraper),
        ("text/html", "4.01", JHoveHtmlScraper),
        ("application/xhtml+xml", "1.0", JHoveHtmlScraper),
    ]
)
def test_is_supported_deny(mime, ver, class_):
    """Test is_supported method, allow only known versions."""
    assert class_.is_supported(mime, ver, True)
    assert class_.is_supported(mime, None, True)
    assert not class_.is_supported(mime, ver, False)
    assert not class_.is_supported(mime, "foo", True)
    assert not class_.is_supported("foo", ver, True)


@pytest.mark.parametrize(
    ["mime", "ver", "class_"],
    [
        ("text/plain", "", JHoveUtf8Scraper)
    ]
)
def test_is_supported_utf8(mime, ver, class_):
    """Test is_supported method, utf8 scraper."""
    assert not class_.is_supported(mime, ver, True)
    assert not class_.is_supported(mime, None, True)
    assert not class_.is_supported(mime, ver, False)
    assert not class_.is_supported(mime, "foo", True)
    assert not class_.is_supported("foo", ver, True)


@pytest.mark.parametrize(
    ["filename", "scraper_class", "result_dict", "filetype"],
    [
        ("valid_1987a.gif", JHoveGifScraper,
         {"purpose": "Test forcing correct MIME type and version for gif",
          "stdout_part": "MIME type and version not scraped, using",
          "stderr_part": ""},
         {"given_mimetype": "image/gif", "given_version": "1987a",
          "expected_mimetype": "image/gif", "expected_version": "1987a",
          "correct_mimetype": "image/gif"}),
        ("valid_1987a.gif", JHoveGifScraper,
         {"purpose": "Test forcing supported but erroneous file type",
          "stdout_part": "Well-Formed and valid",
          "stderr_part": ""},
         {"given_mimetype": "image/gif", "given_version": "1989a",
          "expected_mimetype": "image/gif", "expected_version": "1989a",
          "correct_mimetype": "image/gif"}),
        ("valid_1987a.gif", JHoveGifScraper,
         {"purpose": "Test forcing wrong MIME type and version for gif",
          "stdout_part": "MIME type and version not scraped, using",
          "stderr_part": "not supported by this scraper"},
         {"given_mimetype": "wrong/mime", "given_version": "0",
          "expected_mimetype": "wrong/mime", "expected_version": "0",
          "correct_mimetype": "image/gif"}),
        ("valid_1987a.gif", JHoveGifScraper,
         {"purpose": "Test forcing only version for gif",
          "stdout_part": "Well-Formed and valid",
          "stderr_part": ""},
         {"given_mimetype": None, "given_version": "0",
          "expected_mimetype": "image/gif", "expected_version": "1987a",
          "correct_mimetype": "image/gif"}),
        ("valid_6.0.tif", JHoveTiffScraper,
         {"purpose": "Test forcing correct MIME type and version for tiff.",
          "stdout_part": "MIME type and version not scraped, using",
          "stderr_part": ""},
         {"given_mimetype": "image/tiff", "given_version": "6.0",
          "expected_mimetype": "image/tiff", "expected_version": "6.0",
          "correct_mimetype": "image/tiff"}),
        ("valid_6.0.tif", JHoveTiffScraper,
         {"purpose": "Test forcing wrong MIME type for tiff.",
          "stdout_part": "MIME type and version not scraped, using",
          "stderr_part": "not supported by this scraper"},
         {"given_mimetype": "wrong/mime", "given_version": "6.0",
          "expected_mimetype": "wrong/mime", "expected_version": "6.0",
          "correct_mimetype": "image/tiff"}),
        ("valid_6.0.tif", JHoveTiffScraper,
         {"purpose": "Test forcing only version for tiff.",
          "stdout_part": "Well-Formed and valid",
          "stderr_part": ""},
         {"given_mimetype": None, "given_version": "99.9",
          "expected_mimetype": "image/tiff", "expected_version": "6.0",
          "correct_mimetype": "image/tiff"}),
        ("valid_1.4.pdf", JHovePdfScraper,
         {"purpose": "Test forcing the correct MIME type and version.",
          "stdout_part": "MIME type and version not scraped, using",
          "stderr_part": ""},
         {"given_mimetype": "application/pdf", "given_version": "1.4",
          "expected_mimetype": "application/pdf", "expected_version": "1.4",
          "correct_mimetype": "application/pdf"}),
        ("valid_1.4.pdf", JHovePdfScraper,
         {"purpose": "Test forcing supported but wrong file type.",
          "stdout_part": "MIME type and version not scraped, using",
          "stderr_part": ""},
         {"given_mimetype": "application/pdf", "given_version": "1.2",
          "expected_mimetype": "application/pdf", "expected_version": "1.2",
          "correct_mimetype": "application/pdf"}),
        ("valid_1.4.pdf", JHovePdfScraper,
         {"purpose": "Test forcing unsupported MIME type.",
          "stdout_part": "MIME type not scraped, using",
          "stderr_part": "not supported"},
         {"given_mimetype": "wrong/mime", "given_version": None,
          "expected_mimetype": "wrong/mime", "expected_version": "1.4",
          "correct_mimetype": "application/pdf"}),
        ("valid_1.4.pdf", JHovePdfScraper,
         {"purpose": "Test forcing only version.",
          "stdout_part": "Well-Formed and valid",
          "stderr_part": ""},
         {"given_mimetype": None, "given_version": "99.9",
          "expected_mimetype": "application/pdf", "expected_version": "1.4",
          "correct_mimetype": "application/pdf"}),
        ("valid_1.01.jpg", JHoveJpegScraper,
         {"purpose": "Forcing correct MIME type and version for jpeg files",
          "stdout_part": "MIME type and version not scraped, using",
          "stderr_part": ""},
         {"given_mimetype": "image/jpeg", "given_version": "1.01",
          "expected_mimetype": "image/jpeg", "expected_version": "1.01",
          "correct_mimetype": "image/jpeg"}),
        ("valid_1.01.jpg", JHoveJpegScraper,
         {"purpose": "Forcing unsupported MIME type and version for jpg files",
          "stdout_part": "MIME type and version not scraped, using",
          "stderr_part": ""},
         {"given_mimetype": "wrong/mime", "given_version": "99",
          "expected_mimetype": "wrong/mime", "expected_version": "99",
          "correct_mimetype": "image/jpeg"}),
        ("valid_1.01.jpg", JHoveJpegScraper,
         {"purpose": "Forcing only version for jpeg files",
          "stdout_part": "Well-Formed and valid",
          "stderr_part": ""},
         {"given_mimetype": None, "given_version": "99",
          "expected_mimetype": "image/jpeg", "expected_version": "(:unav)",
          "correct_mimetype": "image/jpeg"}),
        ("valid_1.01.jpg", JHoveJpegScraper,
         {"purpose": "Forcing only MIME type for jpeg files",
          "stdout_part": "MIME type not scraped",
          "stderr_part": ""},
         {"given_mimetype": "image/jpeg", "given_version": None,
          "expected_mimetype": "image/jpeg", "expected_version": "(:unav)",
          "correct_mimetype": "image/jpeg"}),
        ("valid_4.01.html", JHoveHtmlScraper,
         {"purpose": "Forcing correct MIME type and version for html file",
          "stdout_part": "MIME type and version not scraped, using",
          "stderr_part": ""},
         {"given_mimetype": "text/html", "given_version": "4.01",
          "expected_mimetype": "text/html", "expected_version": "4.01",
          "correct_mimetype": "text/html", "charset": "UTF-8"}),
        ("valid_4.01.html", JHoveHtmlScraper,
         {"purpose": "Forcing wrong but supported file type for html file",
          "stdout_part": "MIME type and version not scraped, using",
          "stderr_part": ""},
         {"given_mimetype": "application/xhtml+xml", "given_version": "1.0",
          "expected_mimetype": "application/xhtml+xml",
          "expected_version": "1.0",
          "correct_mimetype": "application/xhtml+xmp", "charset": "UTF-8"}),
        ("valid_4.01.html", JHoveHtmlScraper,
         {"purpose": "Forcing unsupported MIME type for html file",
          "stdout_part": "MIME type not scraped, using",
          "stderr_part": ""},
         {"given_mimetype": "text/plain", "given_version": None,
          "expected_mimetype": "text/plain", "expected_version": "4.01",
          "correct_mimetype": "text/html", "charset": "UTF-8"}),
        ("valid_4.01.html", JHoveHtmlScraper,
         {"purpose": "Forcing only version for html file",
          "stdout_part": "Well-Formed and valid",
          "stderr_part": ""},
         {"given_mimetype": None, "given_version": "99",
          "expected_mimetype": "text/html", "expected_version": "4.01",
          "correct_mimetype": "text/html", "charset": "UTF-8"}),
        ("valid__wav.wav", JHoveWavScraper,
         {"purpose": "Forcing supported MIME type and version for wav files",
          "stdout_part": "MIME type and version not scraped",
          "stderr_part": ""},
         {"given_mimetype": "audio/x-wav", "given_version": "2",
          "expected_mimetype": "audio/x-wav", "expected_version": "2",
          "correct_mimetype": "audio/x-wav"}),
        ("valid__wav.wav", JHoveWavScraper,
         {"purpose": "Forcing unsupported MIME type for wav files",
          "stdout_part": "MIME type not scraped",
          "stderr_part": ""},
         {"given_mimetype": "wrong/mime", "given_version": None,
          "expected_mimetype": "wrong/mime", "expected_version": "(:unav)",
          "correct_mimetype": "audio/x-wav"}),
        ("valid__wav.wav", JHoveWavScraper,
         {"purpose": "Forcing only version for wav files",
          "stdout_part": "Well-Formed and valid",
          "stderr_part": ""},
         {"given_mimetype": None, "given_version": "99",
          "expected_mimetype": "audio/x-wav", "expected_version": "(:unav)",
          "correct_mimetype": "audio/x-wav"}),
    ]
)
def test_forced_filetype(filename, scraper_class, result_dict, filetype,
                         evaluate_scraper):
    """
    Test all JHove scrapers with supported and unsupported forced filetypes.

    At least forcing the corrext MIME type and version (well-formed),
    usupported MIME type (not well-formed, the wrong MIME type reported) and
    forcing only the version (no effect on scraping results) are tested.
    """
    correct = force_correct_filetype(filename, result_dict,
                                     filetype)
    params = {"mimetype": filetype["given_mimetype"],
              "version": filetype["given_version"]}
    params["charset"] = filetype.get("charset", None)
    scraper = scraper_class(correct.filename, True, params)
    scraper.scrape_file()

    evaluate_scraper(scraper, correct)


@pytest.mark.parametrize(
    ["filename", "charset", "well_formed"],
    [("tests/data/application_xhtml+xml/valid_1.0.xhtml", "UTF-8", True),
     ("tests/data/application_xhtml+xml/valid_1.0.xhtml", "ISO-8859-15",
      False),
     ("tests/data/text_html/valid_4.01.html", "UTF-8", True),
     ("tests/data/text_html/valid_4.01.html", "ISO-8859-15", False),
     ("tests/data/text_html/valid_4.01.html", None, False)
    ]
)
def test_charset(filename, charset, well_formed):
    """
    Test charset parameter.
    """
    params = {"charset": charset}
    scraper = JHoveHtmlScraper(filename, True, params)
    scraper.scrape_file()
    assert scraper.well_formed == well_formed
    if charset:
        if well_formed:
            assert not scraper.errors()
        else:
            assert partial_message_included(
                "Found encoding declaration", scraper.errors())
    else:
        assert partial_message_included("encoding not defined",
                                        scraper.errors())
