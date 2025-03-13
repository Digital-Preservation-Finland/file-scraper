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

import PIL
import pytest

from file_scraper.defaults import UNAV, UNAP
from file_scraper.pil.pil_scraper import PilScraper
from tests.common import (parse_results, partial_message_included)

VALID_MSG = "successfully"
INVALID_MSG = "Error in analyzing file."

STREAM_VALID_L = {
    "bps_unit": "integer",
    "bps_value": UNAV,
    "colorspace": UNAV,
    "height": UNAV,
    "width": UNAV,
    "samples_per_pixel": "1",
    "compression": UNAV}

STREAM_VALID_LA = {
    "bps_unit": "integer",
    "bps_value": UNAV,
    "colorspace": UNAV,
    "height": UNAV,
    "width": UNAV,
    "samples_per_pixel": "2",
    "compression": UNAV}

STREAM_VALID_RGB = {
    "bps_unit": "integer",
    "bps_value": UNAV,
    "colorspace": UNAV,
    "height": UNAV,
    "width": UNAV,
    "samples_per_pixel": "3",
    "compression": UNAV}

STREAM_VALID_RGBA = {
    "bps_unit": "integer",
    "bps_value": UNAV,
    "colorspace": UNAV,
    "height": UNAV,
    "width": UNAV,
    "samples_per_pixel": "4",
    "compression": UNAV}

GIF_APPEND = {
    "bps_unit": "integer",
    "bps_value": UNAV,
    "colorspace": UNAV,
    "compression": UNAV,
    "height": UNAV,
    "mimetype": "image/gif",
    "samples_per_pixel": "1",
    "stream_type": "image",
    "version": UNAV,
    "width": UNAV}

STREAM_INVALID = {}


def _new_pil_version(version):
    """Check whether PIL version is given version or newer.
    """
    ver = float(".".join(PIL.__version__.split(".", 2)[:2]))
    return True if ver >= version else False


@pytest.mark.parametrize(
    ["filename", "result_dict"],
    [
        ("valid_6.0.tif", {
            "purpose": "Test valid file.",
            "streams": {0: STREAM_VALID_RGB.copy()}}),
        ("valid_6.0_multiple_pages_and_modes.tif", {
            "purpose": "Test valid multiple tiff file.",
            "streams": {0: STREAM_VALID_L.copy(),
                        1: STREAM_VALID_LA.copy(),
                        2: STREAM_VALID_RGB.copy(),
                        3: STREAM_VALID_RGBA.copy()}}),
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
                            result_dict, False)
    if correct.well_formed is not False:
        correct.stdout_part = VALID_MSG
        correct.stderr_part = ""
    else:
        correct.stdout_part = ""
        correct.stderr_part = INVALID_MSG
    scraper = PilScraper(filename=correct.filename, mimetype="image/tiff")
    scraper.scrape_file()

    if correct.well_formed is not False:
        for index, _ in enumerate(correct.streams):
            correct.streams[index]["version"] = UNAV
        evaluate_scraper(scraper, correct)
    else:
        assert scraper.well_formed is False
        assert partial_message_included(correct.stdout_part,
                                        scraper.messages())
        assert partial_message_included(correct.stderr_part,
                                        scraper.errors())
        assert not scraper.streams


@pytest.mark.parametrize(
    ["filename", "result_dict"],
    [
        ("valid_1.4.dng", {
            "purpose": "Test valid file.",
            "streams": {0: STREAM_VALID_RGB.copy()}}),
        ("invalid_1.4_edited_header.dng", {
            "purpose": "Test invalid file with corrupted header.",
            "streams": {0: STREAM_INVALID.copy()}}),
        ("invalid__empty.dng", {
            "purpose": "Test empty file.",
            "streams": {0: STREAM_INVALID.copy()}})
    ]
)
def test_scraper_dng(filename, result_dict, evaluate_scraper):
    """
    Test scraper with dng files.

    :filename: Test file name
    :result_dict: Result dict containing the test purpose and expected streams"

    """
    correct = parse_results(filename, "image/x-adobe-dng", result_dict, False)

    if correct.well_formed is not False:
        correct.stdout_part = VALID_MSG
        correct.stderr_part = ""
    else:
        correct.stdout_part = ""
        correct.stderr_part = INVALID_MSG
    correct.streams[0]["version"] = UNAV
    scraper = PilScraper(filename=correct.filename,
                         mimetype="image/x-adobe-dng")
    scraper.scrape_file()
    if correct.well_formed is not False:
        evaluate_scraper(scraper, correct)
    else:
        assert scraper.well_formed is False
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
            "streams": {0: STREAM_VALID_RGB.copy()}}),
        ("invalid_1.01_data_changed.jpg", {
            "purpose": "Test image data change in file.",
            "inverse": True,
            "streams": {0: STREAM_VALID_RGB.copy()}}),
        ("invalid_1.01_no_start_marker.jpg", {
            "purpose": "Test start marker change in file.",
            "inverse": True,
            "streams": {0: STREAM_VALID_RGB.copy()}}),
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
                            result_dict, False)
    correct.streams[0]["version"] = UNAV

    # Newer PIL versions can not open some invalid JPEG files.
    # Older PIL versions open some invalid JPEG files successfully.
    # However, PIL does not validate images.
    if result_dict.get("inverse") and _new_pil_version(8.2):
        correct.well_formed = False

    if correct.well_formed is not False:
        correct.stdout_part = VALID_MSG
        correct.stderr_part = ""
    else:
        correct.stdout_part = ""
        correct.stderr_part = INVALID_MSG

    scraper = PilScraper(filename=correct.filename, mimetype="image/jpeg")
    scraper.scrape_file()

    if correct.well_formed is not False:
        evaluate_scraper(scraper, correct)
    else:
        assert scraper.well_formed is False
        assert partial_message_included(correct.stdout_part,
                                        scraper.messages())
        assert partial_message_included(correct.stderr_part,
                                        scraper.errors())
        assert not scraper.streams


@pytest.mark.parametrize(
    ["filename", "result_dict"],
    [
        ("valid__jpylyzer_reference.jp2", {
            "purpose": "Test valid file.",
            "streams": {0: STREAM_VALID_RGB.copy()}}),
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
                            result_dict, False)
    if correct.well_formed is not False:
        correct.stdout_part = VALID_MSG
        correct.stderr_part = ""
    else:
        correct.stdout_part = ""
        correct.stderr_part = INVALID_MSG
    scraper = PilScraper(filename=correct.filename, mimetype="image/jp2")
    scraper.scrape_file()

    if correct.well_formed is not False:
        evaluate_scraper(scraper, correct)
    else:
        assert scraper.well_formed is False
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
            "streams": {0: STREAM_VALID_RGB.copy()}}),
        ("valid_1.2_LA.png", {
            "purpose": "Test valid gray+alpha file.",
            "streams": {0: STREAM_VALID_LA.copy()}}),
        ("invalid_1.2_no_IEND.png", {
            "purpose": "Test without IEND.",
            "inverse": True,
            "streams": {0: STREAM_VALID_RGB.copy()}}),
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
                            result_dict, False)
    correct.streams[0]["version"] = UNAV
    if correct.well_formed is not False:
        correct.stdout_part = VALID_MSG
        correct.stderr_part = ""
    else:
        correct.stdout_part = ""
        correct.stderr_part = INVALID_MSG
    scraper = PilScraper(filename=correct.filename, mimetype="image/png")
    scraper.scrape_file()

    if correct.well_formed is not False:
        evaluate_scraper(scraper, correct)
    else:
        assert scraper.well_formed is False
        assert partial_message_included(correct.stdout_part,
                                        scraper.messages())
        assert partial_message_included(correct.stderr_part, scraper.errors())
        assert not scraper.streams


@pytest.mark.parametrize(
    ["filename", "result_dict"],
    [
        ("valid_1987a.gif", {
            "purpose": "Test valid file.",
            "streams": {0: STREAM_VALID_RGB.copy()}}),
        ("valid_1989a.gif", {
            "purpose": "Test valid file.",
            "streams": {0: STREAM_VALID_RGB.copy(),
                        1: GIF_APPEND.copy(),
                        2: GIF_APPEND.copy()}}),
        ("invalid_1987a_broken_header.gif", {
            "purpose": "Test invalid header.",
            "streams": {0: STREAM_INVALID.copy()}}),
        ("invalid_1987a_truncated.gif", {
            "purpose": "Test truncated file.",
            "inverse": True,
            "streams": {0: STREAM_VALID_RGB.copy()}}),
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
    correct = parse_results(filename, "image/gif", result_dict, False)
    # GIF is always a palette index image.
    correct.streams[0]["samples_per_pixel"] = "1"
    for stream in correct.streams.values():
        stream["version"] = UNAV

    # Newer PIL versions can not open some invalid GIF files.
    # Older PIL versions open some invalid GIF files successfully.
    # However, PIL does not validate images.
    if result_dict.get("inverse") and _new_pil_version(6.1):
        correct.well_formed = False

    if correct.well_formed is not False:
        correct.stdout_part = VALID_MSG
        correct.stderr_part = ""
    else:
        correct.stdout_part = ""
        correct.stderr_part = INVALID_MSG

    scraper = PilScraper(filename=correct.filename, mimetype="image/gif")
    scraper.scrape_file()

    if correct.well_formed is not False:
        evaluate_scraper(scraper, correct)
    else:
        assert scraper.well_formed is False
        assert partial_message_included(correct.stdout_part,
                                        scraper.messages())
        assert partial_message_included(correct.stderr_part,
                                        scraper.errors())
        assert not scraper.streams


@pytest.mark.parametrize(
    ["filename", "result_dict"],
    [
        ("valid__lossless.webp", {
            "purpose": "Test valid lossless file",
            "streams": {0: STREAM_VALID_RGB.copy()}}),
        ("valid__lossy.webp", {
            "purpose": "Test valid lossy file",
            "streams": {0: STREAM_VALID_RGB.copy()}}),
        ("invalid__empty.webp", {
            "purpose": "Test empty file",
            "streams": {0: STREAM_VALID_RGB.copy()}}),
        ("invalid__lossless_with_lossy_header.webp", {
            "purpose": "Test lossless file with VP8 header",
            "streams": {0: STREAM_VALID_RGB.copy()}}),
        ("invalid__missing_bitstream.webp", {
            "purpose": "Test lossless file without bitstream (VP8L header)",
            "streams": {0: STREAM_VALID_RGB.copy()}}),
        ("invalid__missing_icc_profile.webp", {
            "purpose": "Test file without icc profile header",
            "streams": {0: STREAM_VALID_RGB.copy()}}),
        ("invalid__missing_image_data.webp", {
            "purpose": "Test file with byte missing from image data",
            "streams": {0: STREAM_VALID_RGB.copy()}}),
    ]
)
def test_scraper_webp(filename, result_dict, evaluate_scraper):
    """Test screaper with WebP files.

    :filename: Test file name
    :result_dict: Result dic containing the test purpose and expected streams
    """
    correct = parse_results(filename, "image/webp", result_dict, False)

    if correct.well_formed is not False:
        correct.stdout_part = VALID_MSG
        correct.stderr_part = ""
    else:
        correct.stdout_part = ""
        correct.stderr_part = INVALID_MSG

    correct.streams[0]["version"] = UNAP
    scraper = PilScraper(filename=correct.filename, mimetype="image/webp")
    scraper.scrape_file()

    if correct.well_formed is not False:
        evaluate_scraper(scraper, correct)
    else:
        assert scraper.well_formed is False
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
        ("image/webp", "")
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
