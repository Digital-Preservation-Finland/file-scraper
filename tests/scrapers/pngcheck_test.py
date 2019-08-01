"""
Test the file_scraper.scrapers.pngcheck module

This module tests that:
    - MIME type, version, streams and well-formedness of png files are scraped
      correctly.
    - For well-formed files, scraper messages contains 'OK' and there are no
      errors.
    - For non-well-formed files, scraper error is recorded.
    - When well-formedness is not checked, scraper messages contain 'Skipping
      scraper' and well_formed is None.
    - MIME type image/png is supported with version 1.2, None or a made up
      version when well-formedness is checked.
    - When well-formedness is not checked, image/png 1.2 is not supported.
    - A made up MIME type is not supported.
    - MIME type and/or version forcing works.
"""
from __future__ import unicode_literals

import pytest
import six

from file_scraper.pngcheck.pngcheck_scraper import PngcheckScraper
from tests.common import parse_results, force_correct_filetype

MIMETYPE = "image/png"


@pytest.mark.parametrize(
    ["filename", "result_dict"],
    [
        ("valid_1.2.png", {
            "purpose": "Test valid file."}),
        ("invalid_1.2_no_IEND.png", {
            "purpose": "Test without IEND."}),
        ("invalid_1.2_no_IHDR.png", {
            "purpose": "Test without IHDR."}),
        ("invalid_1.2_wrong_CRC.png", {
            "purpose": "Test wrong CRC."}),
        ("invalid_1.2_wrong_header.png", {
            "purpose": "Test invalid header."}),
        ("invalid__empty.png", {
            "purpose": "Test empty file."})
    ]
)
def test_scraper(filename, result_dict, evaluate_scraper):
    """Test scraper."""
    correct = parse_results(filename, MIMETYPE,
                            result_dict, True)
    scraper = PngcheckScraper(correct.filename, True, correct.params)
    scraper.scrape_file()
    correct.version = None
    correct.streams[0]["version"] = "(:unav)"
    correct.streams[0]["mimetype"] = "(:unav)"
    if correct.well_formed:
        correct.stdout_part = "OK"
        correct.stderr_part = ""
    else:
        correct.stdout_part = ""
        correct.stderr_part = "ERROR"

    evaluate_scraper(scraper, correct)


def test_no_wellformed():
    """Test scraper without well-formed check."""
    scraper = PngcheckScraper("tests/data/image_png/valid_1.2.png", False)
    scraper.scrape_file()
    assert "Skipping scraper" in scraper.messages()
    assert scraper.well_formed is None


def test_is_supported():
    """Test is_supported method."""
    mime = MIMETYPE
    ver = "1.2"
    assert PngcheckScraper.is_supported(mime, ver, True)
    assert PngcheckScraper.is_supported(mime, None, True)
    assert not PngcheckScraper.is_supported(mime, ver, False)
    assert PngcheckScraper.is_supported(mime, "foo", True)
    assert not PngcheckScraper.is_supported("foo", ver, True)


@pytest.mark.parametrize(
    ["result_dict", "filetype"],
    [
        ({"purpose": "Test forcing correct MIME type and version",
          "stdout_part": "MIME type and version not scraped, using",
          "stderr_part": ""},
         {"given_mimetype": "image/png",
          "given_version": "1.2",
          "expected_mimetype": "image/png",
          "expected_version": "1.2"}),
        ({"purpose": "Test forcing correct MIME type",
          "stdout_part": "MIME type not scraped, using",
          "stderr_part": ""},
         {"given_mimetype": "image/png",
          "given_version": None,
          "expected_mimetype": "image/png",
          "expected_version": "(:unav)"}),
        ({"purpose": "Test forcing version only (no effect)",
          "stdout_part": "",
          "stderr_part": ""},
         {"given_mimetype": None, "given_version": "1.2",
          "expected_mimetype": "(:unav)", "expected_version": "(:unav)"}),
        ({"purpose": "Test forcing wrong MIME type",
          "stdout_part": "MIME type not scraped, using",
          "stderr_part": "is not supported"},
         {"given_mimetype": "unsupported/mime", "given_version": None,
          "expected_mimetype": "unsupported/mime",
          "expected_version": "(:unav)"})
    ]
)
def test_forced_filetype(result_dict, filetype, evaluate_scraper):
    """
    Test using user-supplied MIME-types and versions.
    """
    filetype[six.text_type("correct_mimetype")] = "image/png"
    correct = force_correct_filetype("valid_1.2.png", result_dict,
                                     filetype, ["(:unav)"])

    params = {"mimetype": filetype["given_mimetype"],
              "version": filetype["given_version"]}
    scraper = PngcheckScraper(correct.filename, True, params)
    scraper.scrape_file()

    evaluate_scraper(scraper, correct)
