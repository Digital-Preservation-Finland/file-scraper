"""
Tests for ExifTool scraper.

This module tests that:
    - MIME type and version of dng files is scraped correctly.
    - For valid files scraper messages contain "successfully".
    - For an empty file, scraper errors contain "File is empty".

"""


import pytest

from file_scraper.exiftool.exiftool_scraper import ExifToolDngScraper
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
def test_scraper_dng(filename, result_dict, evaluate_scraper):
    """
    Test scraper with dng files.

    :filename: Test file name
    :result_dict: Result dict containing test purpose, and parts of expected
                  results of stdout and stderr
    """
    correct = parse_results(filename, "image/x-adobe-dng", result_dict, False)

    scraper = ExifToolDngScraper(filename=correct.filename,
                                 mimetype="image/x-adobe-dng")
    scraper.scrape_file()

    if correct.well_formed is not False:
        evaluate_scraper(scraper, correct)
    else:
        assert not scraper.well_formed
        assert partial_message_included(correct.stdout_part,
                                        scraper.messages())
        assert partial_message_included(correct.stderr_part,
                                        scraper.errors())
