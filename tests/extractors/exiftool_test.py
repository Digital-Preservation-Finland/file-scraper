"""
Tests for ExifTool extractor.

This module tests that:
    - MIME type and version of dng files is scraped correctly.
    - For valid files extractor messages contain "The file was analyzed".
    - For an empty file, extractor errors contain "File is empty".

"""
from collections.abc import Callable
from pathlib import Path

import pytest
from file_scraper.exiftool.exiftool_extractor import ExifToolExtractor

from tests.common import parse_results, partial_message_included


@pytest.mark.parametrize(
    ["filename", "result_dict", "mimetype"],
    [
        (
            "valid_1.4.dng",
            {
                "purpose": "Test valid file",
                "stdout_part": "The file was analyzed",
                "stderr_part": "",
            },
            "image/x-adobe-dng",
        ),
        (
            "invalid__empty.dng",
            {
                "purpose": "Test empty file",
                "stdout_part": "",
                "stderr_part": "File is empty",
            },
            "image/x-adobe-dng",
        ),
        (
            "valid_2.2.1_exif_metadata.jpg",
            {
                "purpose": "Test valid file",
                "stdout_part": "The file was analyzed",
                "stderr_part": "",
            },
            "image/jpeg",
        ),
        (
            "invalid_2.2_null_terminated_exif_version.jpg",
            {
                "purpose": "Test file with null-terminated ExifVersion",
                "stdout_part": "",
                "stderr_part": "'022' is not 4 characters long",
            },
            "image/jpeg",
        ),
        (
            "valid_1.1_geotiff.tif",
            {
                "purpose": "Test valid GeoTIFF file",
                "stdout_part": "analyzed with ExifToolExtractor",
                "stderr_part": "",
            },
            "image/tiff",
        ),
        (
            "valid_1.1_geotiff_multichannel_32bit.tif",
            {
                "purpose": "Test valid multichannel 32 bit file",
                "stdout_part": "analyzed with ExifToolExtractor",
                "stderr_part": "",
            },
            "image/tiff",
        ),
    ],
)
def test_extractor(
    filename: str,
    result_dict: dict[str, str],
    mimetype: str,
    evaluate_extractor: Callable,
) -> None:
    """Test extractor with DNG, JPEG/Exif and GeoTIFF files.

    :param filename: Test file name
    :param result_dict: Result dict containing test purpose, and parts of
        expected results of stdout and stderr.
    :param mimetype: Test file mimetype
    :param evaluate_extractor: Function to evaluate extractor output.
    """
    correct = parse_results(filename, mimetype, result_dict, False)

    extractor = ExifToolExtractor(filename=correct.filename, mimetype=mimetype)
    extractor.extract()

    if correct.well_formed is not False:
        evaluate_extractor(extractor, correct)
    else:
        assert not extractor.well_formed
        assert partial_message_included(
            correct.stdout_part, extractor.messages()
        )
        assert partial_message_included(
            correct.stderr_part, extractor.errors()
        )


def test_tools():
    """Test tools return correctly."""
    extractor = ExifToolExtractor(filename=Path("valid_1.4.dng"),
                                   mimetype="image/x-adobe-dng")
    assert extractor.tools() is not None
    assert extractor.tools()["ExifTool"]["version"][0].isdigit()

