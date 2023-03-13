"""
Tests for DPX scraper.

This module tests that:
    - MIME type, version, streams and well-formedness of files are scraped
      correctly using DpxScraper scraper. This is done with a valid file and
      files with different errors in them:
        - empty file
        - file size is larger than is reported in the header
        - last byte of the file is missing
        - header reports little-endian order but contents of the file are
          big-endian
    - the scraper reports MIME type 'image/x-dpx' with version 2.0 as
      supported when full scraping is done
    - the scraper reports other MIME type or version as not supported when
      full scraping is done
    - the scraper reports MIME type 'image/x-dpx' with version 2.0 as not
      supported when only well-formed check is performed
"""
from __future__ import unicode_literals
import os

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
        ("invalid__empty_file.dpx", {
            "purpose": "Test empty file.",
            "stdout_part": "",
            "stderr_part": "Truncated file"}),
        ("invalid_2.0_file_size_error.dpx", {
            "purpose": "Test file size error.",
            "stdout_part": "",
            "stderr_part": "Different file sizes"}),
        ("invalid_2.0_missing_data.dpx", {
            "purpose": "Test missing data.",
            "stdout_part": "",
            "stderr_part": "Different file sizes"}),
        ("invalid_2.0_wrong_endian.dpx", {
            "purpose": "Test wrong endian.",
            "stdout_part": "",
            "stderr_part": "is more than file size"}),
    ]
)
def test_scraper(filename, result_dict, evaluate_scraper):
    """
    Test DPX scraper functionality.

    :filename: Test file name
    :result_dict: Result dict containing purpose of the test, and
                  parts of the expected results of stdout and stderr
    """
    correct = parse_results(filename, MIMETYPE,
                            result_dict, True)
    scraper = DpxScraper(filename=correct.filename, mimetype=MIMETYPE)
    scraper.scrape_file()

    evaluate_scraper(scraper, correct)


@pytest.mark.usefixtures("patch_shell_returncode_fx")
def test_dpx_returns_invalid_return_code():
    """Test that a correct error message is given
    when the tool gives an invalid return code"""
    path = os.path.join("tests/data", MIMETYPE.replace("/", "_"))
    testfile = os.path.join(path, "valid_2.0.dpx")

    scraper = DpxScraper(filename=testfile,
                          mimetype=MIMETYPE)

    scraper.scrape_file()

    assert "DPX returned invalid return code: -1\n" in scraper.errors()


def test_is_supported():
    """Test is_supported method."""
    mime = MIMETYPE
    assert DpxScraper.is_supported(mime, "2.0", True)
    assert DpxScraper.is_supported(mime, None, True)
    assert DpxScraper.is_supported(mime, "1.0", True)
    assert not DpxScraper.is_supported(mime, "2.0", False)
    assert not DpxScraper.is_supported(mime, "3.0", False)
    assert not DpxScraper.is_supported(mime, "foo", True)
    assert not DpxScraper.is_supported("foo", "2.0", True)
