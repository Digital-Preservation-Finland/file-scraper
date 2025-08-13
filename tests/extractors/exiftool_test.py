"""
Tests for ExifTool extractor.

This module tests that:
    - MIME type and version of dng files is scraped correctly.
    - For valid files extractor messages contain "successfully".
    - For an empty file, extractor errors contain "File is empty".

"""
from pathlib import Path

import pytest

from file_scraper.exiftool.exiftool_extractor import ExifToolDngExtractor
from tests.common import (parse_results, partial_message_included)


@pytest.mark.parametrize(
    ["filename", "result_dict"],
    [
        ("valid_1.4.dng", {
            "purpose": "Test valid file",
            "stdout_part": "successfully",
            "stderr_part": ""
            }),
        ("invalid__empty.dng", {
            "purpose": "Test empty file",
            "stdout_part": "",
            "stderr_part": "File is empty"
            })
    ]
)
def test_extractor_dng(filename, result_dict, evaluate_extractor):
    """
    Test extractor with dng files.

    :filename: Test file name
    :result_dict: Result dict containing test purpose, and parts of expected
                  results of stdout and stderr
    """
    correct = parse_results(filename, "image/x-adobe-dng", result_dict, False)

    extractor = ExifToolDngExtractor(filename=correct.filename,
                                   mimetype="image/x-adobe-dng")
    extractor.extract()

    if correct.well_formed is not False:
        evaluate_extractor(extractor, correct)
    else:
        assert not extractor.well_formed
        assert partial_message_included(correct.stdout_part,
                                        extractor.messages())
        assert partial_message_included(correct.stderr_part,
                                        extractor.errors())


def test_tools():
    """
    Test tools return correctly
    """
    extractor = ExifToolDngExtractor(filename=Path("valid_1.4.dng"),
                                   mimetype="image/x-adobe-dng")
    assert extractor.tools() is not None
    assert extractor.tools()["ExifTool"]["version"][0].isdigit()
