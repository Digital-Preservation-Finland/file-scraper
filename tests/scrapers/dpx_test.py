"""
Tests for DPX scraper.

This module tests that:
    - MIME type, version, streams and well-formedness of files are scraped
      correctly using DpxScraper scraper when full well-formed check is
      performed. This is done with a valid file and files with different errors
      in them:
        - empty file
        - file size is larger than is reported in the header
        - last byte of the file is missing
        - header reports little-endian order but contents of the file are
          big-endian
    - forcing MIME type and/or version works.
    - when check_wellformed is set to False, well-formedness is reported as
      None and scraper messages report skipped scraping.
    - the scraper reports MIME type 'image/x-dpx' with version 2.0 as
      supported when full scraping is done
    - the scraper reports other MIME type or version as not supported when
      full scraping is done
    - the scraper reports MIME type 'image/x-dpx' with version 2.0 as not
      supported when only well-formed check is performed
"""
from __future__ import unicode_literals

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
    """Test scraper."""
    correct = parse_results(filename, MIMETYPE,
                            result_dict, True)
    scraper = DpxScraper(correct.filename, True, correct.params)
    scraper.scrape_file()

    evaluate_scraper(scraper, correct)


@pytest.mark.parametrize(
    ["filename", "result_dict", "filetype"],
    [
        ("valid_2.0.dpx", {
            "purpose": "Test not giving either MIME type or version.",
            "stdout_part": "is valid",
            "stderr_part": ""},
         {"given_mimetype": None, "given_version": None,
          "expected_mimetype": "image/x-dpx", "expected_version": "2.0"}),
        ("valid_2.0.dpx", {
            "purpose": "Test forcing the correct MIME type.",
            "stdout_part": "MIME type not scraped",
            "stderr_part": ""},
         {"given_mimetype": "image/x-dpx", "given_version": None,
          "expected_mimetype": "image/x-dpx", "expected_version": "2.0"}),
        ("valid_2.0.dpx", {
            "purpose": "Test forcing supported MIME type and version.",
            "stdout_part": "MIME type and version not scraped",
            "stderr_part": ""},
         {"given_mimetype": "image/x-dpx", "given_version": "2.0",
          "expected_mimetype": "image/x-dpx", "expected_version": "2.0"}),
        ("valid_2.0.dpx", {
            "purpose": "Test forcing unsupported MIME type.",
            "stdout_part": "MIME type not scraped",
            "stderr_part": "is not supported"},
         {"given_mimetype": "forced/mimetype", "given_version": None,
          "expected_mimetype": "forced/mimetype", "expected_version": "2.0"}),
        ("valid_2.0.dpx", {
            "purpose": "Test forcing MIME type and version.",
            "stdout_part": "MIME type and version not scraped",
            "stderr_part": "is not supported"},
         {"given_mimetype": "forced/mimetype", "given_version": "99.9",
          "expected_mimetype": "forced/mimetype", "expected_version": "99.9"}),
        ("valid_2.0.dpx", {
            "purpose": "Test forcing only version (no effect).",
            "stdout_part": "is valid",
            "stderr_part": ""},
         {"given_mimetype": None, "given_version": "99.9",
          "expected_mimetype": "image/x-dpx", "expected_version": "2.0"}),
    ]
)
def test_forcing_filetype(filename, result_dict, filetype, evaluate_scraper):
    """Test forcing scraper to use a given MIME type and/or version."""
    correct = parse_results(filename, MIMETYPE,
                            result_dict, True)
    params = correct.params
    params.update({"mimetype": filetype["given_mimetype"],
                   "version": filetype["given_version"]})
    scraper = DpxScraper(correct.filename, True, params)
    scraper.scrape_file()

    correct.update_mimetype(filetype["expected_mimetype"])
    correct.update_version(filetype["expected_version"])

    if correct.mimetype != "image/x-dpx":
        correct.well_formed = False

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
