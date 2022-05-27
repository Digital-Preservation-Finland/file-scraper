"""
Tests for ExifTool scraper.

This module tests that:
    - MIME type and version of dng files is tested correctly.

"""

from __future__ import unicode_literals

import pytest

from file_scraper.exiftool.exiftool_scraper import ExifToolDngScraper
from tests.common import parse_results


@pytest.mark.parametrize(
    ["filename", "result_dict"],
    [
        ("valid_1.4.dng", {
            "purpose": "Test valid file",
            "stdout_part": "successfully",
            "stderr_part": ""
            })
    ]
)
def test_scraper(filename, result_dict, evaluate_scraper):
    """
    Test scraper with valid dng files.

    :filename: Test file name
    :result_dict: Result dict containing test purpose, and parts of expected
                  results of stdout and stderr
    """
    correct = parse_results(filename, "image/x-adobe-dng", result_dict, True)

    scraper = ExifToolDngScraper(filename=correct.filename,
                                 mimetype="image/x-adobe-dng")
    scraper.scrape_file()
    evaluate_scraper(scraper, correct)
