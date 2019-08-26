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
    - Forcing MIME type and/or version works.
"""
from __future__ import unicode_literals

import pytest

from file_scraper.pil.pil_scraper import PilScraper
from tests.common import (parse_results, force_correct_filetype,
                          partial_message_included)

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
    """Test scraper with tiff files."""
    correct = parse_results(filename, "image/tiff",
                            result_dict, True)
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
            correct.streams[index]["version"] = "(:unav)"
        evaluate_scraper(scraper, correct)
    else:
        assert not scraper.well_formed
        assert partial_message_included(correct.stdout_part, scraper.messages())
        assert partial_message_included(correct.stderr_part, scraper.errors())
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
        assert partial_message_included(correct.stdout_part, scraper.messages())
        assert partial_message_included(correct.stderr_part, scraper.errors())
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
        assert partial_message_included(correct.stdout_part, scraper.messages())
        assert partial_message_included(correct.stderr_part, scraper.errors())
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
        assert partial_message_included(correct.stdout_part, scraper.messages())
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
        assert partial_message_included(correct.stdout_part, scraper.messages())
        assert partial_message_included(correct.stderr_part, scraper.errors())
        assert not scraper.streams


def test_no_wellformed():
    """Test scraper without well-formed check."""
    scraper = PilScraper("tests/data/image_gif/valid_1987a.gif", False)
    scraper.scrape_file()
    assert not partial_message_included("Skipping scraper", scraper.messages())
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


def run_filetype_test(filename, result_dict, filetype, evaluate_scraper,
                      allowed_mimetypes=[]):
    """
    Runs scraper result evaluation for a scraper with forced MIME type/version

    :filename: Name of the file, not containing the tests/data/mime_type/ part
    :result_dict: Result dict to be given to Correct
    :filetype: A dict containing the forced, expected and real file types under
               the following keys:
                * given_mimetype: the forced MIME type
                * given_version: the forced version
                * expected_mimetype: the expected resulting MIME type
                * expected_version: the expected resulting version
                * correct_mimetype: the real MIME type of the file
    """
    correct = force_correct_filetype(filename, result_dict,
                                     filetype, allowed_mimetypes)
    if correct.mimetype == "application/xhtml+xml":
        correct.streams[0]["stream_type"] = "text"

    if filetype["given_mimetype"]:
        mimetype_guess = filetype["given_mimetype"]
    else:
        mimetype_guess = filetype["correct_mimetype"]
    params = {"mimetype": filetype["given_mimetype"],
              "version": filetype["given_version"],
              "mimetype_guess": mimetype_guess}
    scraper = PilScraper(correct.filename, True, params)
    scraper.scrape_file()

    evaluate_scraper(scraper, correct)


@pytest.mark.parametrize(
    ["filename", "mimetype", "version", "version_result",
     "extra_valid_mimetypes"],
    [
        ("valid_6.0_multiple_tiffs.tif", "image/tiff", "6.0", "(:unav)", []),
        ("valid_1.2.png", "image/png", "1.2", "(:unav)", ["image/jp2",
                                                          "image/gif"]),
        ("valid.jp2", "image/jp2", "(:unav)", "(:unav)", []),
        ("valid_1989a.gif", "image/gif", "1989a", "(:unav)", []),
        ("valid_1.01.jpg", "image/jpeg", "1.01", "(:unav)", []),
    ]
)
def test_forced_filetype(filename, mimetype, version, version_result,
                         extra_valid_mimetypes, evaluate_scraper):
    """
    Tests the simple cases of file type forcing.

    Here, the following cases are tested for one file type scraped using each
    metadata model class supported by PilScraper:
        - Force the scraper to use the correct MIME type and version, which
          should always result in the given MIME type and version and the file
          should be well-formed.
        - Force the scraper to use the correct MIME type, which should always
          result in the given MIME type and the version the metadata model
          would normally return.
        - Give forced version without MIME type, which should result in the
          scraper running normally and not affect its results or messages.
        - Force the scraper to use an unsupported MIME type, which should
          result in an error message being logged and the scraper reporting
          the file as not well-formed.
    """
    # pylint: disable=too-many-arguments
    result_dict = {"purpose": "Test forcing correct MIME type and version",
                   "stdout_part": "MIME type and version not scraped, using",
                   "stderr_part": ""}
    filetype_dict = {"given_mimetype": mimetype,
                     "given_version": version,
                     "expected_mimetype": mimetype,
                     "expected_version": version,
                     "correct_mimetype": mimetype}
    run_filetype_test(filename, result_dict, filetype_dict, evaluate_scraper)

    for other_mimetype in extra_valid_mimetypes:
        result_dict = {"purpose": "Test forcing other MIME type also scraped "
                                  "by this scraper "
                                  "({})".format(other_mimetype),
                       "stdout_part": "MIME type not scraped, using",
                       "stderr_part": ""}
        filetype_dict = {"given_mimetype": other_mimetype,
                         "given_version": None,
                         "expected_mimetype": other_mimetype,
                         "expected_version": version_result,
                         "correct_mimetype": mimetype}
        run_filetype_test(filename, result_dict, filetype_dict,
                          evaluate_scraper, [other_mimetype])

    result_dict = {"purpose": "Test forcing correct MIME type without version",
                   "stdout_part": "MIME type not scraped, using",
                   "stderr_part": ""}
    filetype_dict = {"given_mimetype": mimetype,
                     "given_version": None,
                     "expected_mimetype": mimetype,
                     "expected_version": version_result,
                     "correct_mimetype": mimetype}
    run_filetype_test(filename, result_dict, filetype_dict, evaluate_scraper)

    result_dict = {"purpose": "Test forcing version only (no effect)",
                   "stdout_part": "The file was analyzed successfully",
                   "stderr_part": ""}
    filetype_dict = {"given_mimetype": None,
                     "given_version": "99.9",
                     "expected_mimetype": mimetype,
                     "expected_version": version_result,
                     "correct_mimetype": mimetype}
    run_filetype_test(filename, result_dict, filetype_dict, evaluate_scraper)

    result_dict = {"purpose": "Test forcing wrong MIME type",
                   "stdout_part": "MIME type not scraped, using",
                   "stderr_part": "MIME type not supported by this scraper"}
    filetype_dict = {"given_mimetype": "unsupported/mime",
                     "given_version": None,
                     "expected_mimetype": "unsupported/mime",
                     "expected_version": version_result,
                     "correct_mimetype": mimetype}
    run_filetype_test(filename, result_dict, filetype_dict, evaluate_scraper)
