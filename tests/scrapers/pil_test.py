"""
Tests for PIL scraper.

This module tests that:
    - The MIME type, version, streams and well-formedness are scraped
      correctly from well-formed tif, jpg, jp2, png and gif files with scraper
      messages containing 'successfully'
    - These are also scraped correctly from files of same type with errors
      such as missing data, broken header or empty file, with scraper errors
      containing 'Error in analyzing file'.
    - The following MIME type and version pairs are supported both with and
      without well-formedness check:
        - image/tiff, 6.0
        - image/jpeg, 1.01
        - image/jp2, ''
        - image/png, 1.2
        - image/gif, 1987a
    - These MIME types are also supported with None or a made up version.
    - A made up MIME type with any of these versions is not supported.
"""
from __future__ import unicode_literals

import pytest

from file_scraper.pil.pil_scraper import PilScraper
from tests.common import (parse_results, partial_message_included)

VALID_MSG = "successfully"
INVALID_MSG = "Error in analyzing file."

STREAM_VALID = {
    "bps_unit": "integer",
    "bps_value": "(:unav)",
    "colorspace": "(:unav)",
    "height": "(:unav)",
    "width": "(:unav)",
    "samples_per_pixel": "3",
    "compression": "(:unav)"}

GIF_APPEND = {
    "bps_unit": "integer",
    "bps_value": "(:unav)",
    "colorspace": "(:unav)",
    "compression": "(:unav)",
    "height": "(:unav)",
    "mimetype": "image/gif",
    "samples_per_pixel": "1",
    "stream_type": "image",
    "version": "(:unav)",
    "width": "(:unav)"}

STREAM_INVALID = {}


@pytest.mark.parametrize(
    ["filename", "result_dict"],
    [
        ("valid_6.0.tif", {
            "purpose": "Test valid file.",
            "streams": {0: STREAM_VALID.copy()}}),
        ("valid_6.0_multiple_tiffs.tif", {
            "purpose": "Test valid multiple tiff file.",
            "streams": {0: STREAM_VALID.copy(),
                        1: STREAM_VALID.copy(),
                        2: STREAM_VALID.copy()}}),
        ("invalid_6.0_payload_altered.tif", {
            "purpose": "Test payload altered in file.",
            "streams": {0: STREAM_INVALID.copy()}}),
        ("invalid_6.0_wrong_byte_order.tif", {
            "purpose": "Test wrong byte order in file.",
            "streams": {0: STREAM_INVALID.copy()}}),
        ("invalid__empty.tif", {
            "purpose": "Test empty file.",
            "streams": {0: STREAM_INVALID.copy()}}),
    ]
)
def test_scraper_tif(filename, result_dict, evaluate_scraper):
    """
    Test scraper with tiff files.

    :filename: Test file name
    :result_dict: Result dict containing the test purpose, parts of
                  expected results of stdout and stderr, and expected streams
    """
    correct = parse_results(filename, "image/tiff",
                            result_dict, True)
    if correct.well_formed:
        correct.stdout_part = VALID_MSG
        correct.stderr_part = ""
    else:
        correct.stdout_part = ""
        correct.stderr_part = INVALID_MSG
    scraper = PilScraper(filename=correct.filename, mimetype="image/tiff")
    scraper.scrape_file()

    if correct.well_formed:
        for index in range(0, len(correct.streams)):
            correct.streams[index]["version"] = "(:unav)"
        evaluate_scraper(scraper, correct)
    else:
        assert not scraper.well_formed
        assert partial_message_included(correct.stdout_part,
                                        scraper.messages())
        assert partial_message_included(correct.stderr_part,
                                        scraper.errors())
        assert not scraper.streams


@pytest.mark.parametrize(
    ["filename", "result_dict"],
    [
        ("valid_1.01.jpg", {
            "purpose": "Test valid file.",
            "streams": {0: STREAM_VALID.copy()}}),
        ("invalid_1.01_data_changed.jpg", {
            "purpose": "Test image data change in file.",
            "inverse": True,
            "streams": {0: STREAM_VALID.copy()}}),
        ("invalid_1.01_no_start_marker.jpg", {
            "purpose": "Test start marker change in file.",
            "inverse": True,
            "streams": {0: STREAM_VALID.copy()}}),
        ("invalid__empty.jpg", {
            "purpose": "Test empty file.",
            "streams": {0: STREAM_INVALID.copy()}}),
    ]
)
def test_scraper_jpg(filename, result_dict, evaluate_scraper):
    """
    Test scraper with jpeg files.

    :filename: Test file name
    :result_dict: Result dict containing the test purpose, parts of
                  expected results of stdout and stderr, and expected streams
    """
    correct = parse_results(filename, "image/jpeg",
                            result_dict, True)
    correct.streams[0]["mimetype"] = "image/jpeg"
    correct.streams[0]["version"] = "(:unav)"
    if correct.well_formed:
        correct.stdout_part = VALID_MSG
        correct.stderr_part = ""
    else:
        correct.stdout_part = ""
        correct.stderr_part = INVALID_MSG
    scraper = PilScraper(filename=correct.filename, mimetype="image/jpeg")
    scraper.scrape_file()

    if correct.well_formed:
        evaluate_scraper(scraper, correct)
    else:
        assert not scraper.well_formed
        assert partial_message_included(correct.stdout_part,
                                        scraper.messages())
        assert partial_message_included(correct.stderr_part,
                                        scraper.errors())
        assert not scraper.streams


@pytest.mark.parametrize(
    ["filename", "result_dict"],
    [
        ("valid.jp2", {
            "purpose": "Test valid file.",
            "streams": {0: STREAM_VALID.copy()}}),
        ("invalid__data_missing.jp2", {
            "purpose": "Test data missing file.",
            "streams": {0: STREAM_INVALID.copy()}}),
        ("invalid__empty.jp2", {
            "purpose": "Test empty file.",
            "streams": {0: STREAM_INVALID.copy()}}),
    ]
)
def test_scraper_jp2(filename, result_dict, evaluate_scraper):
    """
    Test scraper with jp2 files.

    :filename: Test file name
    :result_dict: Result dict containing the test purpose, parts of
                  expected results of stdout and stderr, and expected streams
    """
    correct = parse_results(filename, "image/jp2",
                            result_dict, True)
    if correct.well_formed:
        correct.stdout_part = VALID_MSG
        correct.stderr_part = ""
    else:
        correct.stdout_part = ""
        correct.stderr_part = INVALID_MSG
    scraper = PilScraper(filename=correct.filename, mimetype="image/jp2")
    scraper.scrape_file()

    if correct.well_formed:
        evaluate_scraper(scraper, correct)
    else:
        assert not scraper.well_formed
        assert partial_message_included(correct.stdout_part,
                                        scraper.messages())
        assert partial_message_included(correct.stderr_part,
                                        scraper.errors())
        assert not scraper.streams


@pytest.mark.parametrize(
    ["filename", "result_dict"],
    [
        ("valid_1.2.png", {
            "purpose": "Test valid file.",
            "streams": {0: STREAM_VALID.copy()}}),
        ("invalid_1.2_no_IEND.png", {
            "purpose": "Test without IEND.",
            "inverse": True,
            "streams": {0: STREAM_VALID.copy()}}),
        ("invalid_1.2_no_IHDR.png", {
            "purpose": "Test without IHDR.",
            "streams": {0: STREAM_INVALID.copy()}}),
        ("invalid_1.2_wrong_CRC.png", {
            "purpose": "Test wrong CRC.",
            "streams": {0: STREAM_INVALID.copy()}}),
        ("invalid_1.2_wrong_header.png", {
            "purpose": "Test invalid header.",
            "streams": {0: STREAM_INVALID.copy()}}),
        ("invalid__empty.png", {
            "purpose": "Test empty file.",
            "streams": {0: STREAM_INVALID.copy()}}),
    ]
)
def test_scraper_png(filename, result_dict, evaluate_scraper):
    """
    Test scraper with png files.

    :filename: Test file name
    :result_dict: Result dict containing the test purpose, parts of
                  expected results of stdout and stderr, and expected streams
    """
    correct = parse_results(filename, "image/png",
                            result_dict, True)
    correct.streams[0]["version"] = "(:unav)"
    if correct.well_formed:
        correct.stdout_part = VALID_MSG
        correct.stderr_part = ""
    else:
        correct.stdout_part = ""
        correct.stderr_part = INVALID_MSG
    scraper = PilScraper(filename=correct.filename, mimetype="image/png")
    scraper.scrape_file()

    if correct.well_formed:
        evaluate_scraper(scraper, correct)
    else:
        assert not scraper.well_formed
        assert partial_message_included(correct.stdout_part,
                                        scraper.messages())
        assert partial_message_included(correct.stderr_part, scraper.errors())
        assert not scraper.streams


@pytest.mark.parametrize(
    ["filename", "result_dict"],
    [
        ("valid_1987a.gif", {
            "purpose": "Test valid file.",
            "streams": {0: STREAM_VALID.copy()}}),
        ("valid_1989a.gif", {
            "purpose": "Test valid file.",
            "streams": {0: STREAM_VALID.copy(),
                        1: GIF_APPEND.copy(),
                        2: GIF_APPEND.copy()}}),
        ("invalid_1987a_broken_header.gif", {
            "purpose": "Test invalid header.",
            "streams": {0: STREAM_INVALID.copy()}}),
        ("invalid_1987a_truncated.gif", {
            "purpose": "Test truncated file.",
            "inverse": True,
            "streams": {0: STREAM_VALID.copy()}}),
        ("invalid_1989a_broken_header.gif", {
            "purpose": "Test invalid header.",
            "streams": {0: STREAM_INVALID.copy()}}),
        ("invalid_1989a_truncated.gif", {
            "purpose": "Test truncated file.",
            "streams": {0: STREAM_INVALID.copy()}}),
        ("invalid__empty.gif", {
            "purpose": "Test empty file.",
            "streams": {0: STREAM_INVALID.copy()}})
    ]
)
def test_scraper_gif(filename, result_dict, evaluate_scraper):
    """
    Test scraper with gif files.

    :filename: Test file name
    :result_dict: Result dict containing the test purpose, parts of
                  expected results of stdout and stderr, and expected streams
    """
    correct = parse_results(filename, "image/gif", result_dict, True)
    # GIF is an index image
    if correct.well_formed:
        correct.streams[0]["samples_per_pixel"] = "1"
    for stream in correct.streams.values():
        stream["version"] = "(:unav)"
    if correct.well_formed:
        correct.stdout_part = VALID_MSG
        correct.stderr_part = ""
    else:
        correct.stdout_part = ""
        correct.stderr_part = INVALID_MSG
    scraper = PilScraper(filename=correct.filename, mimetype="image/gif")
    scraper.scrape_file()

    if correct.well_formed:
        evaluate_scraper(scraper, correct)
    else:
        assert not scraper.well_formed
        assert partial_message_included(correct.stdout_part,
                                        scraper.messages())
        assert partial_message_included(correct.stderr_part,
                                        scraper.errors())
        assert not scraper.streams


@pytest.mark.parametrize(
    ["mime", "ver"],
    [
        ("image/tiff", "6.0"),
        ("image/jpeg", "1.01"),
        ("image/jp2", ""),
        ("image/png", "1.2"),
        ("image/gif", "1987a"),
    ]
)
def test_is_supported(mime, ver):
    """
    Test is_supported method.

    :mime: MIME type
    :ver: File format version
    """
    assert PilScraper.is_supported(mime, ver, True)
    assert PilScraper.is_supported(mime, None, True)
    assert PilScraper.is_supported(mime, ver, False)
    assert PilScraper.is_supported(mime, "foo", True)
    assert not PilScraper.is_supported("foo", ver, True)
