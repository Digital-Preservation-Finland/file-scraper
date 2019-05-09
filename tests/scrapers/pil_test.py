"""
Tests for PIL scraper.

This module tests that:
    - The MIME type, version, streams and well-formedness are scraped
      correctly from well-formed tif, jpg, jp2, png and gif files with scraper
      messages containing 'successfully'
    - These are also scraped correctly from files of same type with errors
      such as missing data, broken header or empty file, with scraper errors
      containing 'Error in analyzing file'.
    - If well-formedness is not tested, scraper messages contains 'Skipping
      scraper' and well_formed is None.
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
import pytest
from file_scraper.pil.pil_scraper import PilScraper
from tests.common import parse_results

# TODO remove
from file_scraper.utils import generate_metadata_dict

VALID_MSG = "successfully"
INVALID_MSG = "Error in analyzing file."

STREAM_VALID = {
    "bps_unit": "integer",
    "bps_value": None,
    "colorspace": None,
    "height": None,
    "width": None,
    "samples_per_pixel": "3",
    "compression": None}

GIF_APPEND = {
    "bps_unit": "integer",
    "bps_value": None,
    "colorspace": None,
    "compression": None,
    "height": None,
    "mimetype": "image/gif",
    "samples_per_pixel": "1",
    "stream_type": "image",
    "version": None,
    "width": None}

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
    """Test scraper with tiff files."""
    correct = parse_results(filename, "image/tiff",
                            result_dict, True)
    correct.version = None
    correct.streams[0]["version"] = None
    if correct.well_formed:
        correct.stdout_part = VALID_MSG
        correct.stderr_part = ""
    else:
        correct.stdout_part = ""
        correct.stderr_part = INVALID_MSG
    scraper = PilScraper(correct.filename, True, correct.params)
    scraper.scrape_file()

    if correct.well_formed:
        for index in range(0, len(correct.streams)):
            correct.streams[index]["mimetype"] = \
                correct.streams[0]["mimetype"]
            correct.streams[index]["stream_type"] = \
                correct.streams[0]["stream_type"]
            correct.streams[index]["version"] = "(:unav)"
        evaluate_scraper(scraper, correct)
    else:
        assert not scraper.well_formed
        assert correct.stdout_part in scraper.messages()
        assert correct.stderr_part in scraper.errors()
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
    """Test scraper with jpeg files."""
    correct = parse_results(filename, "image/jpeg",
                            result_dict, True)
    correct.streams[0]["version"] = "(:unav)"
    if correct.well_formed:
        correct.stdout_part = VALID_MSG
        correct.stderr_part = ""
    else:
        correct.stdout_part = ""
        correct.stderr_part = INVALID_MSG
    scraper = PilScraper(correct.filename, True, correct.params)
    scraper.scrape_file()

    if correct.well_formed:
        evaluate_scraper(scraper, correct)
    else:
        assert not scraper.well_formed
        assert correct.stdout_part in scraper.messages()
        assert correct.stderr_part in scraper.errors()
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
    """Test scraper with jp2 files."""
    correct = parse_results(filename, "image/jp2",
                            result_dict, True)
    correct.streams[0]["version"] = "(:unav)"
    if correct.well_formed:
        correct.stdout_part = VALID_MSG
        correct.stderr_part = ""
    else:
        correct.stdout_part = ""
        correct.stderr_part = INVALID_MSG
    scraper = PilScraper(correct.filename, True, correct.params)
    scraper.scrape_file()

    if correct.well_formed:
        evaluate_scraper(scraper, correct)
    else:
        assert not scraper.well_formed
        assert correct.stdout_part in scraper.messages()
        assert correct.stderr_part in scraper.errors()
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
    """Test scraper with png files."""
    correct = parse_results(filename, "image/png",
                            result_dict, True)
    correct.streams[0]["version"] = "(:unav)"
    if correct.well_formed:
        correct.stdout_part = VALID_MSG
        correct.stderr_part = ""
    else:
        correct.stdout_part = ""
        correct.stderr_part = INVALID_MSG
    scraper = PilScraper(correct.filename, True, correct.params)
    scraper.scrape_file()

    if correct.well_formed:
        evaluate_scraper(scraper, correct)
    else:
        assert not scraper.well_formed
        assert correct.stdout_part in scraper.messages()
        assert correct.stderr_part in scraper.errors()
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
    """Test scraper with gif files."""
    correct = parse_results(filename, "image/gif",
                            result_dict, True)
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
    scraper = PilScraper(correct.filename, True, correct.params)
    scraper.scrape_file()

    if correct.well_formed:
        evaluate_scraper(scraper, correct)
    else:
        assert not scraper.well_formed
        assert correct.stdout_part in scraper.messages()
        assert correct.stderr_part in scraper.errors()
        assert not scraper.streams


def test_no_wellformed():
    """Test scraper without well-formed check."""
    scraper = PilScraper("tests/data/image_gif/valid_1987a.gif", False)
    scraper.scrape_file()
    assert "Skipping scraper" not in scraper.messages()
    assert scraper.well_formed is None


@pytest.mark.parametrize(
    ["mime", "ver", "class_"],
    [
        ("image/tiff", "6.0", PilScraper),
        ("image/jpeg", "1.01", PilScraper),
        ("image/jp2", "", PilScraper),
        ("image/png", "1.2", PilScraper),
        ("image/gif", "1987a", PilScraper),
    ]
)
def test_is_supported(mime, ver, class_):
    """Test is_supported method."""
    assert class_.is_supported(mime, ver, True)
    assert class_.is_supported(mime, None, True)
    assert class_.is_supported(mime, ver, False)
    assert class_.is_supported(mime, "foo", True)
    assert not class_.is_supported("foo", ver, True)
