"""
Tests for ImageMagick scraper.

This module tests that:
    - streams and well-formedness are scraped correctly for tiff files.
        - For valid files containing one or more images, scraper messages
          contain "successfully".
        - For file where payload has been altered, scraper errors contain
          "Failed to read directory at offset 182".
        - For file with wrong byte order reported in the header, scraper errors
          contain "Not a TIFF file, bad version number 10752".
        - For an empty file, scraper errors contain "Cannot read TIFF header."
    - streams and well-formedness are scraped correctly for jpeg files.
        - For well-formed files, scraper messages contain "successfully".
        - For file with altered payload, scraper errors contain "Bogus marker
          length".
        - For file without start marker, scraper errors contain "starts with
          0xff 0xe0".
        - For empty file, scraper errors contain "Empty input file".
    - streams and well-formedness are scraped correctly for jp2 files.
        - For well-formed files, scraper messages contain "successfully".
        - For an empty file or a file with missing data, scraper errors
          contain "unable to decode image file".
    - streams and well-formedness are scraped correctly for png files.
        - For well-formed files, scraper messages contain "successfully".
        - For file with missing IEND or IHDR chunk or wrong CRC, scraper
          errors contain "corrupt image".
        - For file with invalid header, scraper errors contain "improper
          image header".
        - For empty file, scraper errors contain "improper image header".
    - streams and well-formedness are scraped correctly for gif files.
        - For well-formed files with one or more images, scraper messages
          contain "successfully".
        - For images with broken header, scraper errors contains "improper
          image header".
        - For truncated version 1987a file, scraper errors contains "corrupt
          image".
        -For truncated version 1989a file, scraper errors contains "negative
         or zero image size".
        - For empty file, scraper errors contains "imporoper image header".
    - When well-formedness is not checked, scraper messages contains "Skipping
      scraper" and well_formed is None.
    - With or without well-formedness check, the following MIME type and
      version pairs are supported by both WandScraper and their corresponding
      metadata models:
        - image/tiff, 6.0
        - image/jpeg, 1.01
        - image/jp2, ''
        - image/png, 1.2
        - image/gif, 1987a
    - All these MIME types are also supported when None or a made up version
      is given as the version.
    - A made up MIME type is not supported.
    - MIME type and/or version forcing works.
"""
from __future__ import unicode_literals

import os
import pytest
import six

from file_scraper.wand.wand_model import WandImageMeta, WandTiffMeta
from file_scraper.wand.wand_scraper import WandScraper
from tests.common import parse_results, force_correct_filetype

STREAM_VALID = {
    "bps_unit": None,
    "bps_value": "8",
    "colorspace": "srgb",
    "height": "6",
    "samples_per_pixel": "(:unav)",
    "width": "10"}

GIF_APPEND = {
    "bps_unit": None,
    "bps_value": "8",
    "colorspace": "srgb",
    "compression": "lzw",
    "height": "1",
    "mimetype": "image/gif",
    "samples_per_pixel": "(:unav)",
    "stream_type": "image",
    "version": None,
    "width": "1"}


@pytest.mark.parametrize(
    ["filename", "result_dict"],
    [
        ("valid_6.0.tif", {
            "purpose": "Test valid file.",
            "streams": {0: STREAM_VALID.copy()},
            "stdout_part": "successfully",
            "stderr_part": ""}),
        ("valid_6.0_multiple_tiffs.tif", {
            "purpose": "Test valid multiple tiff file.",
            "streams": {0: STREAM_VALID.copy(),
                        1: STREAM_VALID.copy(),
                        2: STREAM_VALID.copy()},
            "stdout_part": "successfully",
            "stderr_part": ""})
    ]
)
def test_scraper_tif(filename, result_dict, evaluate_scraper):
    """Test scraper with valid tiff files."""
    correct = parse_results(filename, "image/tiff",
                            result_dict, True)
    for index in range(0, len(correct.streams)):
        correct.streams[index]["compression"] = "zip"
        correct.streams[index]["byte_order"] = "little endian"
        correct.streams[index]["mimetype"] = \
            correct.streams[0]["mimetype"]
        correct.streams[index]["stream_type"] = \
            correct.streams[0]["stream_type"]
        correct.streams[index]["version"] = "(:unav)"

    scraper = WandScraper(correct.filename)
    scraper.scrape_file()
    evaluate_scraper(scraper, correct)


@pytest.mark.parametrize(
    ["filename", "result_dict"],
    [
        ("valid_1.01.jpg", {
            "purpose": "Test valid file.",
            "streams": {0: STREAM_VALID.copy()},
            "stdout_part": "successfully",
            "stderr_part": ""}),
    ]
)
def test_scraper_jpg(filename, result_dict, evaluate_scraper):
    """Test scraper with jpeg files."""
    correct = parse_results(filename, "image/jpeg",
                            result_dict, True)
    if correct.well_formed:
        correct.streams[0]["compression"] = "jpeg"
    correct.streams[0]["version"] = "(:unav)"

    scraper = WandScraper(correct.filename)
    scraper.scrape_file()
    evaluate_scraper(scraper, correct)


@pytest.mark.parametrize(
    ["filename", "result_dict"],
    [
        ("valid.jp2", {
            "purpose": "Test valid file.",
            "streams": {0: STREAM_VALID.copy()},
            "stdout_part": "successfully",
            "stderr_part": ""}),
    ]
)
def test_scraper_jp2(filename, result_dict, evaluate_scraper):
    """Test scraper with jp2 files."""
    correct = parse_results(filename, "image/jp2",
                            result_dict, True)
    if correct.well_formed:
        correct.streams[0]["compression"] = "jpeg2000"
        correct.streams[0]["colorspace"] = "rgb"
    correct.version = None

    scraper = WandScraper(correct.filename)
    scraper.scrape_file()
    evaluate_scraper(scraper, correct)


@pytest.mark.parametrize(
    ["filename", "result_dict"],
    [
        ("valid_1.2.png", {
            "purpose": "Test valid file.",
            "streams": {0: STREAM_VALID.copy()},
            "stdout_part": "successfully",
            "stderr_part": ""}),
    ]
)
def test_scraper_png(filename, result_dict, evaluate_scraper):
    """Test scraper with png files."""
    correct = parse_results(filename, "image/png",
                            result_dict, True)
    if correct.well_formed:
        correct.streams[0]["compression"] = "zip"
    correct.streams[0]["version"] = "(:unav)"
    correct.version = None

    scraper = WandScraper(correct.filename)
    scraper.scrape_file()
    evaluate_scraper(scraper, correct)


@pytest.mark.parametrize(
    ["filename", "result_dict"],
    [
        ("valid_1987a.gif", {
            "purpose": "Test valid file.",
            "streams": {0: STREAM_VALID.copy()},
            "stdout_part": "successfully",
            "stderr_part": ""}),
        ("valid_1989a.gif", {
            "purpose": "Test valid file.",
            "streams": {0: STREAM_VALID.copy(),
                        1: GIF_APPEND.copy(),
                        2: GIF_APPEND.copy()},
            "stdout_part": "successfully",
            "stderr_part": ""}),
    ]
)
def test_scraper_gif(filename, result_dict, evaluate_scraper):
    """Test scraper with gif files."""
    correct = parse_results(filename, "image/gif",
                            result_dict, True)
    if correct.well_formed:
        correct.streams[0]["compression"] = "lzw"
    for stream in correct.streams.values():
        stream["version"] = "(:unav)"

    scraper = WandScraper(correct.filename)
    scraper.scrape_file()
    evaluate_scraper(scraper, correct)


@pytest.mark.parametrize(
    ["filename", "mimetype", "stderr_part"],
    [
        ("invalid_6.0_payload_altered.tif", "image/tiff",
         "Failed to read directory at offset 182"),
        ("invalid_6.0_wrong_byte_order.tif", "image/tiff",
         "Not a TIFF file, bad version number 10752"),
        ("invalid__empty.tif", "image/tiff",
         "Cannot read TIFF header."),
        ("invalid_1.01_data_changed.jpg", "image/jpeg",
         "Bogus marker length"),
        ("invalid_1.01_no_start_marker.jpg", "image/jpeg",
         "starts with 0xff 0xe0"),
        ("invalid__empty.jpg", "image/jpeg",
         "Empty input file"),
        ("invalid__data_missing.jp2", "image/jp2",
         "unable to decode image file"),
        ("invalid__empty.jp2", "image/jp2",
         "unable to decode image file"),
        ("invalid_1.2_no_IEND.png", "image/png",
         "corrupt image"),
        ("invalid_1.2_no_IHDR.png", "image/png",
         "corrupt image"),
        ("invalid_1.2_wrong_CRC.png", "image/png",
         "corrupt image"),
        ("invalid_1.2_wrong_header.png", "image/png",
         "improper image header"),
        ("invalid__empty.png", "image/png",
         "improper image header"),
        ("invalid_1987a_broken_header.gif", "image/gif",
         "improper image header"),
        ("invalid_1987a_truncated.gif", "image/gif",
         "corrupt image"),
        ("invalid_1989a_broken_header.gif", "image/gif",
         "improper image header"),
        ("invalid_1989a_truncated.gif", "image/gif",
         "negative or zero image size"),
        ("invalid__empty.gif", "image/gif",
         "improper image header")
    ]
)
def test_scraper_invalid(filename, mimetype, stderr_part):
    """Test WandScraper with invalid tiff files."""
    scraper = WandScraper(os.path.join("tests/data/",
                                       mimetype.replace("/", "_"),
                                       filename))
    scraper.scrape_file()

    assert not scraper.streams
    assert scraper.info()["class"] == "WandScraper"
    assert not scraper.messages()
    assert stderr_part in scraper.errors()
    assert not scraper.well_formed


def test_no_wellformed():
    """Test scraper without well-formed check."""
    scraper = WandScraper("tests/data/image_tiff/valid_6.0.tif",
                          False)
    scraper.scrape_file()
    assert "Skipping scraper" not in scraper.messages()
    assert scraper.well_formed is None


@pytest.mark.parametrize(
    ["mime", "ver", "class_"],
    [
        ("image/tiff", "6.0", WandTiffMeta),
        ("image/jpeg", "1.01", WandImageMeta),
        ("image/jp2", "", WandImageMeta),
        ("image/png", "1.2", WandImageMeta),
        ("image/gif", "1987a", WandImageMeta),
    ]
)
def test_model_is_supported(mime, ver, class_):
    """Test is_supported method for WandTiffMeta and WandImageMeta."""
    assert class_.is_supported(mime, ver)
    assert class_.is_supported(mime, None)
    assert class_.is_supported(mime, "foo")
    assert not class_.is_supported("foo", ver)


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
def test_scraper_is_supported(mime, ver):
    """Test is_supported method for WandScraper"""
    assert WandScraper.is_supported(mime, ver, True)
    assert WandScraper.is_supported(mime, None, True)
    assert WandScraper.is_supported(mime, ver, False)
    assert WandScraper.is_supported(mime, "foo", True)
    assert not WandScraper.is_supported("foo", ver, True)


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

    if filetype["given_mimetype"]:
        mimetype_guess = filetype["given_mimetype"]
    else:
        mimetype_guess = filetype["correct_mimetype"]
    params = {"mimetype": filetype["given_mimetype"],
              "version": filetype["given_version"],
              "mimetype_guess": mimetype_guess}
    scraper = WandScraper(correct.filename, True, params)
    scraper.scrape_file()

    evaluate_scraper(scraper, correct)


@pytest.mark.parametrize(
    ["filename", "mimetype", "version", "extra_mimetypes"],
    [
        ("valid_1.2.png", "image/png", "1.2", ["image/jpeg", "image/jp2",
                                               "image/gif"]),
        ("valid_1.01.jpg", "image/jpeg", "1.01", []),
        ("valid.jp2", "image/jp2", "(:unav)", []),
        ("valid_1987a.gif", "image/gif", "1987a", []),
        ("valid_6.0.tif", "image/tiff", "6.0", []),
    ]
)
def test_forced_filetype(filename, mimetype, version, extra_mimetypes,
                         evaluate_scraper):
    """
    Tests the simple cases of file type forcing.

    Here, the following cases are tested for one file type scraped using each
    metadata model class supported by WandScraper:
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
    version_result = "(:unav)"

    result_dict = {"purpose": "Test forcing correct MIME type and version",
                   "stdout_part": "MIME type and version not scraped, using",
                   "stderr_part": ""}
    filetype_dict = {"given_mimetype": mimetype,
                     "given_version": version,
                     "expected_mimetype": mimetype,
                     "expected_version": version,
                     "correct_mimetype": mimetype}
    run_filetype_test(filename, result_dict, filetype_dict, evaluate_scraper)

    for alternative_mimetype in extra_mimetypes:
        result_dict = {"purpose": "Test forcing MIME type {}, which is "
                                  "supported but not the correct MIME "
                                  "type".format(alternative_mimetype),
                       "stdout_part": "MIME type not scraped, using",
                       "stderr_part": ""}
        filetype_dict = {"given_mimetype": alternative_mimetype,
                         "given_version": None,
                         "expected_mimetype": alternative_mimetype,
                         "expected_version": version_result,
                         "correct_mimetype": mimetype}
        run_filetype_test(filename, result_dict, filetype_dict,
                          evaluate_scraper, [alternative_mimetype])

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
                   "stderr_part": "is not supported"}
    filetype_dict = {"given_mimetype": "unsupported/mime",
                     "given_version": None,
                     "expected_mimetype": "unsupported/mime",
                     "expected_version": version_result,
                     "correct_mimetype": mimetype}
    run_filetype_test(filename, result_dict, filetype_dict, evaluate_scraper)
