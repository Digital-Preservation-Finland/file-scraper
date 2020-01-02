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
from tests.common import (parse_results, partial_message_included)

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
    scraper = PngcheckScraper(filename=correct.filename, mimetype="image/png")
    scraper.scrape_file()
    correct.version = None
    correct.streams[0]["version"] = "(:unav)"
    correct.streams[0]["mimetype"] = "(:unav)"
    if correct.well_formed:
        correct.stdout_part = "OK"
        correct.stderr_part = ""
    else:
        correct.stdout_part = ""
        correct.stderr_part = "Failed:"

    evaluate_scraper(scraper, correct)


def test_no_wellformed():
    """Test scraper without well-formed check."""
    scraper = PngcheckScraper(filename="tests/data/image_png/valid_1.2.png",
                              mimetype="image/png",
                              check_wellformed=False)
    scraper.scrape_file()
    assert partial_message_included("Skipping scraper", scraper.messages())
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
