"""
Tests for DPX extractor.

This module tests that:
    - MIME type, version, streams and well-formedness of files are scraped
      correctly using DpxExtractor extractor. This is done with a valid file and
      files with different errors in them:
        - empty file
        - file size is larger than is reported in the header
        - last byte of the file is missing
        - header reports little-endian order but contents of the file are
          big-endian
    - the extractor reports MIME type 'image/x-dpx' with version 2.0 as
      supported when full scraping is done
    - the extractor reports other MIME type or version as not supported when
      full scraping is done
    - the extractor reports MIME type 'image/x-dpx' with version 2.0 as not
      supported when only well-formed check is performed
"""
import re
from pathlib import Path

import pytest
from tests.common import parse_results
from file_scraper.dpx.dpx_extractor import DpxExtractor

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
def test_extractor(filename, result_dict, evaluate_extractor):
    """
    Test DPX extractor functionality.

    :filename: Test file name
    :result_dict: Result dict containing purpose of the test, and
                  parts of the expected results of stdout and stderr
    """
    correct = parse_results(filename, MIMETYPE,
                            result_dict, True)
    extractor = DpxExtractor(filename=correct.filename, mimetype=MIMETYPE)
    extractor.extract()

    evaluate_extractor(extractor, correct)


def test_dpx_returns_invalid_return_code():
    """Test that a correct error message is given
    when the tool gives an invalid return code"""
    path = Path("tests/data", MIMETYPE.replace("/", "_"))
    testfile = path / "invalid_2.0_missing_data.dpx"

    extractor = DpxExtractor(filename=testfile,
                           mimetype=MIMETYPE)

    extractor.extract()
    extractor.errors()

    assert "Different file sizes from header" in extractor.errors()[0]


def test_is_supported():
    """Test is_supported method."""
    mime = MIMETYPE
    assert DpxExtractor.is_supported(mime, "2.0", True)
    assert DpxExtractor.is_supported(mime, None, True)
    assert DpxExtractor.is_supported(mime, "1.0", True)
    assert not DpxExtractor.is_supported(mime, "2.0", False)
    assert not DpxExtractor.is_supported(mime, "3.0", False)
    assert not DpxExtractor.is_supported(mime, "foo", True)
    assert not DpxExtractor.is_supported("foo", "2.0", True)


def test_tools():
    """ Test that tools were unknown """

    extractor = DpxExtractor(filename=Path(""), mimetype="")
    assert re.fullmatch(r"\d+\.\d+\.\d+", extractor.tools()["dpx-validator"]["version"])
