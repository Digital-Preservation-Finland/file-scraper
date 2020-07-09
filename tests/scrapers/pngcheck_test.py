"""
Test the file_scraper.scrapers.pngcheck module

This module tests that:
    - MIME type, version, streams and well-formedness of png files are scraped
      correctly.
    - For well-formed files, scraper messages contains 'OK' and there are no
      errors.
    - For non-well-formed files, scraper error is recorded.
    - MIME type image/png is supported with version 1.2, None or a made up
      version when well-formedness is checked.
    - When well-formedness is not checked, image/png 1.2 is not supported.
    - A made up MIME type is not supported.
"""
from __future__ import unicode_literals

import pytest

from file_scraper.defaults import UNAV
from file_scraper.pngcheck.pngcheck_scraper import PngcheckScraper
from tests.common import parse_results

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
    """
    Test pngcheck scraper.

    :filename: Test file name
    :result_dict: Dict containing purpose of the test
    """
    correct = parse_results(filename, MIMETYPE,
                            result_dict, True)
    scraper = PngcheckScraper(filename=correct.filename, mimetype="image/png")
    scraper.scrape_file()
    correct.version = None
    correct.update_mimetype(UNAV)
    correct.update_version(UNAV)
    correct.streams[0]["stream_type"] = UNAV
    if correct.well_formed:
        correct.stdout_part = "OK"
        correct.stderr_part = ""
    else:
        correct.stdout_part = ""
        correct.stderr_part = "Failed:"

    evaluate_scraper(scraper, correct)


def test_is_supported():
    """Test is_supported method."""
    mime = MIMETYPE
    ver = "1.2"
    assert PngcheckScraper.is_supported(mime, ver, True)
    assert PngcheckScraper.is_supported(mime, None, True)
    assert not PngcheckScraper.is_supported(mime, ver, False)
    assert PngcheckScraper.is_supported(mime, "foo", True)
    assert not PngcheckScraper.is_supported("foo", ver, True)
