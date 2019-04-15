"""
Tests for DPX scraper.

This module tests that:
    - MIME type, version, streams and well-formedness of files are scraped
      correctly using DpxScraper scraper when full well-formed check is performed.
      This is done with a valid file and files with different errors in them:
        - empty file
        - file size is larger than is reported in the header
        - last byte of the file is missing
        - header reports little-endian order but contents of the file are
          big-endian
    - when check_wellformed is set to False, well-formedness is reported as
      None and scraper messages report skipped scraping.
    - the scraper reports MIME type 'image/x-dpx' with version 2.0 as
      supported when full scraping is done
    - the scraper reports other MIME type or version as not supported when
      full scraping is done
    - the scraper reports MIME type 'image/x-dpx' with version 2.0 as not
      supported when only well-formed check is performed
"""
import pytest
from tests.common import parse_results
from file_scraper.dpx.dpx_scraper import DpxScraper

MIMETYPE = "image/x-dpx"


@pytest.mark.parametrize(
    ["filename", "result_dict"],
    [
        ("valid_2.0.dpx", {
            "purpose": "Test valid file.",
            "stdout_part": "is valid",
            "stderr_part": ""}),
        ("invalid_2.0_empty_file.dpx", {
            "purpose": "Test empty file.",
            "stdout_part": "",
            "stderr_part": "Truncated file"}),
        ("invalid_2.0_file_size_error.dpx", {
            "purpose": "Test file size error.",
            "stdout_part": "",
            "stderr_part": "differs from filesystem size"}),
        ("invalid_2.0_missing_data.dpx", {
            "purpose": "Test missing data.",
            "stdout_part": "",
            "stderr_part": "differs from filesystem size"}),
        ("invalid_2.0_wrong_endian.dpx", {
            "purpose": "Test wrong endian.",
            "stdout_part": "",
            "stderr_part": "is more than file size"}),
    ]
)
def test_scraper(filename, result_dict, evaluate_scraper):
    """Test scraper."""
    correct = parse_results(filename, MIMETYPE,
                            result_dict, True)
    scraper = DpxScraper(correct.filename, True, correct.params)
    scraper.scrape_file()

    evaluate_scraper(scraper, correct)


def test_no_wellformed():
    """Test scraper without well-formed check."""
    scraper = DpxScraper("tests/data/image_x-dpx/valid_2.0.dpx", False)
    scraper.scrape_file()
    assert "Skipping scraper" in scraper.messages()
    assert scraper.well_formed is None


def test_is_supported():
    """Test is_supported method."""
    mime = MIMETYPE
    ver = "2.0"
    assert DpxScraper.is_supported(mime, ver, True)
    assert DpxScraper.is_supported(mime, None, True)
    assert not DpxScraper.is_supported(mime, ver, False)
    assert not DpxScraper.is_supported(mime, "foo", True)
    assert not DpxScraper.is_supported("foo", ver, True)
