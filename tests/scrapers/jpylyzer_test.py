"""
Tests for Jpylyzer scraper.

This module tests that:
    - Well-formedness of jp2 files is scraped correctly.
    - For valid files scraper messages contain "File is well-formed and valid".
    - For invalid files, scraper errors contain "document is not well-formed".

"""

import pytest

from file_scraper.jpylyzer.jpylyzer_scraper import JpylyzerScraper
from tests.common import (parse_results, partial_message_included)


@pytest.mark.parametrize(
    ["filename", "result_dict"],
    [
        ("valid__jpylyzer_reference.jp2", {
            "purpose": "Test valid file",
            "stdout_part": "File is well-formed and valid",
            "stderr_part": ""
            }),
        ("valid__many_qcc_blocks.jp2", {
            "purpose": "Test valid file",
            "stdout_part": "File is well-formed and valid",
            "stderr_part": ""
            }),
        ("invalid__empty.jp2", {
            "purpose": "Test empty file",
            "stdout_part": "",
            "stderr_part": "document is not well-formed"
            }),
        ("invalid__data_missing.jp2", {
            "purpose": "Test invalid file",
            "stdout_part": "",
            "stderr_part": "document is not well-formed"
            })
    ]
)
def test_scraper_jp2(filename, result_dict):
    """
    Test scraper with jp2 files.

    :filename: Test file name
    :result_dict: Result dict containing test purpose, and parts of expected
                  results of stdout and stderr

    """
    correct = parse_results(filename, "image/jp2", result_dict, True)

    scraper = JpylyzerScraper(filename=correct.filename,
                              mimetype="image/jp2")

    scraper.scrape_file()

    assert scraper.well_formed == correct.well_formed

    assert partial_message_included(correct.stdout_part,
                                    scraper.messages())
    assert partial_message_included(correct.stderr_part,
                                    scraper.errors())
