"""
Tests for ImageMagick scraper.

This module tests that:
    - streams and well-formedness are scraped correctly for tiff files.
        - For valid files containing one or more images, scraper messages
          contain "successfully".
        - For file where payload has been altered, scraper errors contain
          "Failed to allocate memory for to read TIFF directory (0 elements of
          12 bytes each)."
        - For file with wrong byte order reported in the header, scraper errors
          contain "Not a TIFF file, bad version number 10752".
        - For an empty file, scraper errors contain "Cannot read TIFF header."
    - streams and well-formedness are scraped correctly for jpeg files.
        - For well-formed files, scraper messages contain "successfully".
        - For file with altered payload, scraper errors contain "Bogus marker
          length".
        - For file without start marker, scraper errors contain "starts with
          0xff 0xe0".
        - For empty file, scraper errors contain "insufficient image data in
          file".
        - For Exif JPEGs, version is interpreted and set
        - For JFIFs, version is unavailable
    - streams and well-formedness are scraped correctly for jp2 files.
        - For well-formed files, scraper messages contain "successfully".
        - For an empty file, scraper errors contain "MagickReadImage returns
          false, but did not raise ImageMagick exception.".
        - For a file with missing data, scraper errors contain "Malformed JP2
          file format: second box must be file type box"
    - streams and well-formedness are scraped correctly for png files.
        - For well-formed files, scraper messages contain "successfully".
        - For file with missing IEND or IHDR chunk scraper errors contain
          "MagickReadImage returns false, but did not raise ImageMagick
          exception.".
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
        - For truncated version 1989a file, scraper errors contains "negative
          or zero image size".
        - For empty file, scraper errors contains "improper image header".
    - WandTiffMeta model is supported for TIFF files, WandExifMeta for JPEG
      files and  WandImageMeta for other image files
    - With or without well-formedness check, the following MIME type and
      version pairs are supported by both WandScraper and their corresponding
      metadata models:
        - image/tiff, 6.0
        - image/jpeg, ''
        - image/jp2, ''
        - image/png, 1.2
        - image/gif, 1987a
    - All these MIME types are also supported when None or a made up version
      is given as the version.
    - A made up MIME type is not supported.
"""
from __future__ import unicode_literals

import os
import pytest

from file_scraper.wand.wand_model import (WandImageMeta, WandTiffMeta,
                                          WandExifMeta)
from file_scraper.wand.wand_scraper import WandScraper
from tests.common import (parse_results, partial_message_included)

STREAM_VALID = {
    "bps_unit": "(:unav)",
    "bps_value": "8",
    "colorspace": "srgb",
    "height": "6",
    "samples_per_pixel": "(:unav)",
    "width": "10",
    "version": "(:unav)"}

EXIF_VALID = {
    "bps_unit": "(:unav)",
    "bps_value": "8",
    "colorspace": "srgb",
    "height": "8",
    "samples_per_pixel": "(:unav)",
    "width": "10",
    "version": "2.2.1"}

GIF_APPEND = {
    "bps_unit": "(:unav)",
    "bps_value": "8",
    "colorspace": "srgb",
    "compression": "lzw",
    "height": "1",
    "mimetype": "image/gif",
    "samples_per_pixel": "(:unav)",
    "stream_type": "image",
    "version": "(:unav)",
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
    """
    Test scraper with valid tiff files.

    :filename: Test file name
    :result_dict: Result dict containing the test purpose, parts of
                  expected results of stdout and stderr, and expected streams
    """
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

    scraper = WandScraper(filename=correct.filename, mimetype="image/tiff")
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
        ("valid_2.2.1_exif_metadata.jpg", {
            "purpose": "Test valid file.",
            "streams": {0: EXIF_VALID.copy()},
            "stdout_part": "successfully",
            "stderr_part": ""}),
        ("valid_2.2.1_exif_no_jfif.jpg", {
            "purpose": "Test valid file.",
            "streams": {0: EXIF_VALID.copy()},
            "stdout_part": "successfully",
            "stderr_part": ""}),
    ]
)
def test_scraper_jpg(filename, result_dict, evaluate_scraper):
    """
    Test scraper with valid jpeg files.

    :filename: Test file name
    :result_dict: Result dict containing the test purpose, parts of
                  expected results of stdout and stderr, and expected streams
    """
    correct = parse_results(filename, "image/jpeg",
                            result_dict, True)
    if correct.well_formed:
        correct.streams[0]["compression"] = "jpeg"

    scraper = WandScraper(filename=correct.filename, mimetype="image/jpeg")
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
    """
    Test scraper with valid jp2 files.

    :filename: Test file name
    :result_dict: Result dict containing the test purpose, parts of
                  expected results of stdout and stderr, and expected streams
    """
    correct = parse_results(filename, "image/jp2",
                            result_dict, True)
    if correct.well_formed:
        correct.streams[0]["compression"] = "jpeg2000"
        correct.streams[0]["colorspace"] = "rgb"
        correct.streams[0]["version"] = "(:unav)"

    scraper = WandScraper(filename=correct.filename, mimetype="image/jp2")
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
    """
    Test scraper with valid png files.

    :filename: Test file name
    :result_dict: Result dict containing the test purpose, parts of
                  expected results of stdout and stderr, and expected streams
    """
    correct = parse_results(filename, "image/png",
                            result_dict, True)
    if correct.well_formed:
        correct.streams[0]["compression"] = "zip"
    correct.streams[0]["version"] = "(:unav)"

    scraper = WandScraper(filename=correct.filename, mimetype="image/png")
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
    """
    Test scraper with valid gif files.

    :filename: Test file name
    :result_dict: Result dict containing the test purpose, parts of
                  expected results of stdout and stderr, and expected streams
    """
    correct = parse_results(filename, "image/gif",
                            result_dict, True)
    if correct.well_formed:
        correct.streams[0]["compression"] = "lzw"
    for stream in correct.streams.values():
        stream["version"] = "(:unav)"

    scraper = WandScraper(filename=correct.filename, mimetype="image/gif")
    scraper.scrape_file()
    evaluate_scraper(scraper, correct)


@pytest.mark.parametrize(
    ["filename", "mimetype", "stderr_part"],
    [
        ("invalid_6.0_payload_altered.tif", "image/tiff",
         "Failed to allocate memory for to read TIFF directory (0 elements of"
         " 12 bytes each)"),
        ("invalid_6.0_wrong_byte_order.tif", "image/tiff",
         "Not a TIFF file, bad version number 10752"),
        ("invalid__empty.tif", "image/tiff",
         "Cannot read TIFF header."),
        ("invalid_1.01_data_changed.jpg", "image/jpeg",
         "Bogus marker length"),
        ("invalid_1.01_no_start_marker.jpg", "image/jpeg",
         "starts with 0xff 0xe0"),
        ("invalid__empty.jpg", "image/jpeg",
         "insufficient image data in file"),
        ("invalid__data_missing.jp2", "image/jp2",
         "Malformed JP2 file format: second box must be file type box"),
        ("invalid__empty.jp2", "image/jp2",
         "MagickReadImage returns false, but did not raise ImageMagick"
         "  exception."),
        ("invalid_1.2_no_IEND.png", "image/png",
         "MagickReadImage returns false, but did not raise ImageMagick"
         "  exception."),
        ("invalid_1.2_no_IHDR.png", "image/png",
         "MagickReadImage returns false, but did not raise ImageMagick"
         "  exception."),
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
    """
    Test WandScraper with invalid files.

    :filename: Test file name
    :mimetype: File MIME type
    :stderr_part: Part of the expected stderr
    """
    scraper = WandScraper(
        filename=os.path.join("tests/data/", mimetype.replace("/", "_"),
                              filename),
        mimetype=mimetype)
    scraper.scrape_file()

    assert not scraper.streams
    assert scraper.info()["class"] == "WandScraper"
    assert not scraper.messages()
    assert partial_message_included(stderr_part, scraper.errors())
    assert not scraper.well_formed


@pytest.mark.parametrize(
    ["mime", "ver", "class_"],
    [
        ("image/tiff", "6.0", WandTiffMeta),
        ("image/jpeg", "", WandExifMeta),
        ("image/jp2", "", WandImageMeta),
        ("image/png", "1.2", WandImageMeta),
        ("image/gif", "1987a", WandImageMeta),
    ]
)
def test_model_is_supported(mime, ver, class_):
    """
    Test is_supported method for WandTiffMeta and WandImageMeta.

    :mime: MIME type
    :ver: File format version
    :class_: Metadata model class
    """
    assert class_.is_supported(mime, ver)
    assert class_.is_supported(mime, None)
    assert class_.is_supported(mime, "foo")
    assert not class_.is_supported("foo", ver)


@pytest.mark.parametrize(
    ["mime", "ver"],
    [
        ("image/tiff", "6.0"),
        ("image/jpeg", ""),
        ("image/jp2", ""),
        ("image/png", "1.2"),
        ("image/gif", "1987a"),
    ]
)
def test_scraper_is_supported(mime, ver):
    """
    Test is_supported method for WandScraper

    :mime: MIME type
    :ver: File format version
    """
    assert WandScraper.is_supported(mime, ver, True)
    assert WandScraper.is_supported(mime, None, True)
    assert WandScraper.is_supported(mime, ver, False)
    assert WandScraper.is_supported(mime, "foo", True)
    assert not WandScraper.is_supported("foo", ver, True)
