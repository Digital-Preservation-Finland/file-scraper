"""
Tests for ImageMagick extractor.

This module tests that:
    - streams and well-formedness are scraped correctly for tiff files.
        - For valid files containing one or more images, extractor messages
          contain "successfully".
        - For file where payload has been altered, extractor errors contain
          "Failed to allocate memory for to read TIFF directory (0 elements of
          12 bytes each)."
        - For file with wrong byte order reported in the header, extractor errors
          contain "Not a TIFF file, bad version number 10752".
        - For an empty file, extractor errors contain "Cannot read TIFF header."
    - streams and well-formedness are scraped correctly for dng files.
        - For valid files, extractor messages contain "successfully".
        - For invalid file with edited header, extractor errors contain "unable
          to open image".
        - For empty file, extractor errors contain "unable to open image".
    - streams and well-formedness are scraped correctly for jpeg files.
        - For well-formed files, extractor messages contain "successfully".
        - For file with altered payload, extractor errors contain "Bogus marker
          length".
        - For file without start marker, extractor errors contain "starts with
          0xff 0xe0".
        - For empty file, extractor errors contain "insufficient image data in
          file".
        - For Exif JPEGs, version is interpreted and set
        - For JFIFs, version is unavailable
    - streams and well-formedness are scraped correctly for jp2 files.
        - For well-formed files, extractor messages contain "successfully".
        - For an empty file, extractor errors contain "MagickReadImage returns
          false, but did not raise ImageMagick exception.".
        - For a file with missing data, extractor errors contain "Malformed JP2
          file format: second box must be file type box"
    - streams and well-formedness are scraped correctly for png files.
        - For well-formed files, extractor messages contain "successfully".
        - For file with missing IEND or IHDR chunk extractor errors contain
          "MagickReadImage returns false, but did not raise ImageMagick
          exception.".
        - For file with invalid header, extractor errors contain "improper
          image header".
        - For empty file, extractor errors contain "improper image header".
    - streams and well-formedness are scraped correctly for gif files.
        - For well-formed files with one or more images, extractor messages
          contain "successfully".
        - For images with broken header, extractor errors contains "improper
          image header".
        - For truncated version 1987a file, extractor errors contains "corrupt
          image".
        - For truncated version 1989a file, extractor errors contains "negative
          or zero image size".
        - For empty file, extractor errors contains "improper image header".
    - streams and well-formedness are scraped correctly for WebP files.
        - For well-formed files, extractor messages contain "successfully".
        - For images with missing headers or image data, extractor errors contain
          "insufficient image data in file".
        - For mismatched headers and data, extractor errors contain "corrupt
          image".
    - WandTiffMeta model is supported for TIFF files, WandExifMeta for
      JPEG files, WandWebPMeta for WebP files and WandImageMeta for other image
      files.
    - Image colorspace detected as "sRGB" will be detected as "RGB" unless
      explicitly expressed by a metadata for colorspace to be sRGB.
    - With or without well-formedness check, the following MIME type and
      version pairs are supported by both WandExtractor and their corresponding
      metadata models:
        - image/tiff, 6.0
        - image/x-adobe-dng, ''
        - image/jpeg, ''
        - image/jp2, ''
        - image/png, 1.2
        - image/gif, 1987a
        - image/webp, ''
    - All these MIME types are also supported when None or a made up version
      is given as the version.
    - A made up MIME type is not supported.
"""

import os

import pytest
import wand

from file_scraper.defaults import UNAV, UNAP
from file_scraper.wand.wand_model import (WandImageMeta, WandTiffMeta,
                                          WandExifMeta, WandWebPMeta)
from file_scraper.wand.wand_extractor import WandExtractor
from tests.common import (parse_results, partial_message_included)

# CentOS 7 uses older version of ImageMagick than RHEL 9
RHEL9 = wand.version.MAGICK_VERSION_INFO > (6, 9, 12, 93)

STREAM_VALID = {
    "bps_unit": UNAV,
    "bps_value": "8",
    "colorspace": "rgb",
    "height": "6",
    "samples_per_pixel": UNAV,
    "width": "10",
    "version": UNAV}

STREAM_VALID_WITH_SRGB = STREAM_VALID.copy()
STREAM_VALID_WITH_SRGB['colorspace'] = 'srgb'

EXIF_VALID = {
    "bps_unit": UNAV,
    "bps_value": "8",
    "colorspace": "rgb",
    "height": "8",
    "samples_per_pixel": UNAV,
    "width": "10",
    "version": "2.2.1"}

GIF_APPEND = {
    "bps_unit": UNAV,
    "bps_value": "8",
    "colorspace": "rgb",
    "compression": "lzw",
    "height": "1",
    "mimetype": "image/gif",
    "samples_per_pixel": UNAV,
    "stream_type": "image",
    "version": UNAV,
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
def test_extractor_tif(filename, result_dict, evaluate_extractor):
    """
    Test extractor with valid tiff files.

    :filename: Test file name
    :result_dict: Result dict containing the test purpose, parts of
                  expected results of stdout and stderr, and expected streams
    """
    correct = parse_results(filename, "image/tiff",
                            result_dict, False)
    for index, _ in enumerate(correct.streams):
        correct.streams[index]["compression"] = "zip"
        correct.streams[index]["byte_order"] = "little endian"
        correct.streams[index]["mimetype"] = \
            correct.streams[0]["mimetype"]
        correct.streams[index]["stream_type"] = \
            correct.streams[0]["stream_type"]
        correct.streams[index]["version"] = UNAV

    extractor = WandExtractor(filename=correct.filename, mimetype="image/tiff")
    extractor.extract()
    evaluate_extractor(extractor, correct)


@pytest.mark.parametrize(
        ["filename", "result_dict"],
        [
            ("valid_1.4.dng", {
                "purpose": "Test valid file",
                "streams": {0:
                            {"version": UNAV,
                             "bps_unit": UNAV,
                             "bps_value": "16",
                             "colorspace": "rgb",
                             "height": "866" if RHEL9 else "1154",
                             "width": "1154" if RHEL9 else "866",
                             "samples_per_pixel": UNAV}},
                "stdout_part": "successfully",
                "stderr_part": ""
                })
        ]
)
def test_extractor_dng(filename, result_dict, evaluate_extractor):
    """
    Test extractor with a valid dng file.

    :filename: Test file name
    :result_dict: Result dict containing test purpose, and parts of expected
              results of stdout and stderr
    """
    correct = parse_results(filename, "image/x-adobe-dng", result_dict, False)
    extractor = WandExtractor(filename=correct.filename,
                            mimetype="image/x-adobe-dng")
    extractor.extract()
    evaluate_extractor(extractor, correct)


@pytest.mark.parametrize(
    ["filename", "result_dict"],
    [
        ("valid_1.01.jpg", {
            "purpose": "Test valid file.",
            "streams": {0: STREAM_VALID.copy()},
            "stdout_part": "successfully",
            "stderr_part": ""}),
        ("valid_1.01_icc_sRGB_profile.jpg", {
            "purpose": "Test valid file.",
            "streams": {0: STREAM_VALID_WITH_SRGB.copy()},
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
def test_extractor_jpg(filename, result_dict, evaluate_extractor):
    """
    Test extractor with valid jpeg files.

    :filename: Test file name
    :result_dict: Result dict containing the test purpose, parts of
                  expected results of stdout and stderr, and expected streams
    """
    correct = parse_results(filename, "image/jpeg",
                            result_dict, False)
    if correct.well_formed is not False:
        correct.streams[0]["compression"] = "jpeg"

    extractor = WandExtractor(filename=correct.filename, mimetype="image/jpeg")
    extractor.extract()
    evaluate_extractor(extractor, correct)


@pytest.mark.parametrize(
    ["filename", "result_dict"],
    [
        ("valid__jpylyzer_reference.jp2", {
            "purpose": "Test valid file.",
            "streams": {0: {
                "version": UNAV,
                "bps_unit": UNAV,
                "bps_value": "8",
                "colorspace": "rgb",
                "height": "8",
                "width": "6",
                "samples_per_pixel": UNAV}},
            "stdout_part": "successfully",
            "stderr_part": ""}),
    ]
)
def test_extractor_jp2(filename, result_dict, evaluate_extractor):
    """
    Test extractor with valid jp2 files.

    :filename: Test file name
    :result_dict: Result dict containing the test purpose, parts of
                  expected results of stdout and stderr, and expected streams
    """
    correct = parse_results(filename, "image/jp2",
                            result_dict, False)
    if correct.well_formed is not False:
        correct.streams[0]["compression"] = "jpeg2000"
        correct.streams[0]["colorspace"] = "rgb"
        correct.streams[0]["version"] = UNAV

    extractor = WandExtractor(filename=correct.filename, mimetype="image/jp2")
    extractor.extract()
    evaluate_extractor(extractor, correct)


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
def test_extractor_png(filename, result_dict, evaluate_extractor):
    """
    Test extractor with valid png files.

    :filename: Test file name
    :result_dict: Result dict containing the test purpose, parts of
                  expected results of stdout and stderr, and expected streams
    """
    correct = parse_results(filename, "image/png",
                            result_dict, False)
    if correct.well_formed is not False:
        correct.streams[0]["compression"] = "zip"
    correct.streams[0]["version"] = UNAV

    extractor = WandExtractor(filename=correct.filename, mimetype="image/png")
    extractor.extract()
    evaluate_extractor(extractor, correct)


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
def test_extractor_gif(filename, result_dict, evaluate_extractor):
    """
    Test extractor with valid gif files.

    :filename: Test file name
    :result_dict: Result dict containing the test purpose, parts of
                  expected results of stdout and stderr, and expected streams
    """
    correct = parse_results(filename, "image/gif",
                            result_dict, False)
    if correct.well_formed is not False:
        correct.streams[0]["compression"] = "lzw"
    for stream in correct.streams.values():
        stream["version"] = UNAV

    extractor = WandExtractor(filename=correct.filename, mimetype="image/gif")
    extractor.extract()
    evaluate_extractor(extractor, correct)


@pytest.mark.parametrize(
    ["filename", "result_dict"],
    [
        ("valid__lossless.webp", {
            "purpose": "Test valid lossless file",
            "streams": {0: STREAM_VALID_WITH_SRGB.copy()},
            "stdout_part": "successfully",
            "stderr_part": ""}),
        ("valid__lossy.webp", {
            "purpose": "Test valid lossy file.",
            "streams": {0: STREAM_VALID_WITH_SRGB.copy()},
            "stdout_part": "successfully",
            "stderr_part": ""}),
    ]
)
def test_extractor_webp(filename, result_dict, evaluate_extractor):
    """
    Test extractor with valid webp files

    :filename: Test file name
    :result_dict: Result dict containing the test purpose, parts of
                  expected results of stdout and stderr, and expected streams
    """
    correct = parse_results(filename, "image/webp", result_dict, False)

    for stream in correct.streams.values():
        stream["version"] = UNAP
        stream["height"] = "16"
        stream["width"] = "16"

    extractor = WandExtractor(filename=correct.filename, mimetype="image/webp")
    extractor.extract()
    evaluate_extractor(extractor, correct)

    if "lossless" in filename:
        assert extractor.streams[0].compression() == "VP8 Lossless"
    if "lossy" in filename:
        assert extractor.streams[0].compression() == "VP8 Lossy"


@pytest.mark.parametrize(("mimetype", "filename", "expected"), [
    ("image/gif", "valid_1987a.gif", "RGB"),
    ("image/gif", "valid_1989a.gif", "RGB"),
    ("image/jp2", "valid__jpylyzer_reference.jp2", "RGB"),
    ("image/jpeg", "valid_1.01.jpg", "RGB"),
    ("image/jpeg", "valid_1.01_icc_sRGB_profile.jpg", "sRGB"),
    ("image/jpeg", "valid_2.2.1_exif_metadata.jpg", "RGB"),
    ("image/jpeg", "valid_2.2.1_exif_no_jfif.jpg", "RGB"),
    ("image/png", "valid_1.2.png", "RGB"),
    ("image/png", "valid_1.2_LA.png", "Gray"),
    ("image/tiff", "valid_6.0.tif", "RGB"),
    ("image/tiff", "valid_6.0_multiple_tiffs.tif", "RGB"),
    ("image/webp", "valid__lossless.webp", "SRGB"),
    ("image/webp", "valid__lossy.webp", "SRGB"),
])
def test_extractor_colorspace(mimetype, filename, expected):
    """
    Test that correct colorspace is returned.
    """
    extractor = WandExtractor(
        filename=os.path.join("tests/data/", mimetype.replace("/", "_"),
                              filename),
        mimetype=mimetype)
    extractor.extract()

    assert extractor.streams[0].colorspace().lower() == expected.lower()


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
         "Read Exception"),
        ("invalid_1.2_no_IHDR.png", "image/png",
         "IHDR: CRC error"),
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
         "improper image header"),
        ("invalid_1.4_edited_header.dng", "image/x-adobe-dng",
         "@ error"),
        ("invalid__empty.dng", "image/x-adobe-dng",
         "@ error"),
        ("invalid__missing_icc_profile.webp", "image/webp",
         "insufficient image data in file"),
        ("invalid__missing_bitstream.webp", "image/webp",
         "insufficient image data in file"),
        ("invalid__empty.webp", "image/webp",
         "insufficient image data in file"),
        ("invalid__missing_image_data.webp", "image/webp",
         "insufficient image data in file"),
        ("invalid__lossless_with_lossy_header.webp", "image/webp",
         "corrupt image")
    ]
)
def test_extractor_invalid(filename, mimetype, stderr_part):
    """
    Test WandExtractor with invalid files.

    :filename: Test file name
    :mimetype: File MIME type
    :stderr_part: Part of the expected stderr
    """

    extractor = WandExtractor(
        filename=os.path.join("tests/data/", mimetype.replace("/", "_"),
                              filename),
        mimetype=mimetype)
    extractor.extract()

    assert not extractor.streams
    assert extractor.info()["class"] == "WandExtractor"
    assert partial_message_included(stderr_part, extractor.errors())
    assert extractor.well_formed is False


@pytest.mark.parametrize(
    ["mime", "ver", "class_"],
    [
        ("image/tiff", "6.0", WandTiffMeta),
        ("image/x-adobe-dng", "", WandImageMeta),
        ("image/jpeg", "", WandExifMeta),
        ("image/jp2", "", WandImageMeta),
        ("image/png", "1.2", WandImageMeta),
        ("image/gif", "1987a", WandImageMeta),
        ("image/webp", "", WandWebPMeta),
    ]
)
def test_model_is_supported(mime, ver, class_):
    """
    Test is_supported method for WandTiffMeta, WandExifMeta and WandImageMeta.

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
        ("image/x-adobe-dng", ""),
        ("image/jpeg", ""),
        ("image/jp2", ""),
        ("image/png", "1.2"),
        ("image/gif", "1987a"),
        ("image/webp", ""),
    ]
)
def test_extractor_is_supported(mime, ver):
    """
    Test is_supported method for WandExtractor

    :mime: MIME type
    :ver: File format version
    """
    assert WandExtractor.is_supported(mime, ver, True)
    assert WandExtractor.is_supported(mime, None, True)
    assert WandExtractor.is_supported(mime, ver, False)
    assert WandExtractor.is_supported(mime, "foo", True)
    assert not WandExtractor.is_supported("foo", ver, True)


def test_tools():
    """:returns: tools used by the extractor as a dictionary"""
    extractor = WandExtractor(filename="", mimetype="")
    assert extractor.tools()["ImageMagick"]["version"][0].isdigit()
