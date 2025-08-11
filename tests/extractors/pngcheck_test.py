"""
Test the file_scraper.pngcheck.pngcheck_extractor module

This module tests that:
    - MIME type, version, streams and well-formedness of png files are scraped
      correctly.
    - For well-formed files, extractor messages contains 'OK' and there are no
      errors.
    - For non-well-formed files, extractor error is recorded.
    - MIME type image/png is supported with version 1.2, None or a made up
      version when well-formedness is checked.
    - When well-formedness is not checked, image/png 1.2 is not supported.
    - A made up MIME type is not supported.
"""

import pytest

from file_scraper.defaults import UNAV
from file_scraper.pngcheck.pngcheck_extractor import PngcheckExtractor
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
def test_extractor(filename, result_dict, evaluate_extractor):
    """
    Test pngcheck extractor.

    :filename: Test file name
    :result_dict: Dict containing purpose of the test
    """
    correct = parse_results(filename, MIMETYPE,
                            result_dict, True)
    extractor = PngcheckExtractor(filename=correct.filename, mimetype="image/png")
    extractor.scrape_file()
    correct.version = None
    correct.update_mimetype(UNAV)
    correct.update_version(UNAV)
    correct.streams[0]["stream_type"] = UNAV
    if correct.well_formed:
        correct.stdout_part = "OK"
        correct.stderr_part = ""
    else:
        correct.stdout_part = ""
        correct.stderr_part = "Pngcheck returned invalid return code: 2\n"

    evaluate_extractor(extractor, correct)


def test_is_supported():
    """Test is_supported method."""
    mime = MIMETYPE
    ver = "1.2"
    assert PngcheckExtractor.is_supported(mime, ver, True)
    assert PngcheckExtractor.is_supported(mime, None, True)
    assert not PngcheckExtractor.is_supported(mime, ver, False)
    assert PngcheckExtractor.is_supported(mime, "foo", True)
    assert not PngcheckExtractor.is_supported("foo", ver, True)


def test_tools():
    """Test extractor tools return correctly something non nullable"""
    correct = parse_results("valid_1.2.png", MIMETYPE, {
            "purpose": "Test valid file."}, True)
    extractor = PngcheckExtractor(filename=correct.filename,
                                mimetype="image/png")
    assert extractor.tools()["PNGcheck"]["version"][0].isdigit()
