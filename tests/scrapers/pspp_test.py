"""
Tests for PSPP scraper.

This module tests that:
    - MIME type, version, streams and well-formedness of por and sav files are
      scraped correctly.
    - When the format of the file is wrong, scraper errors contains 'File is
      not SPSS Portable format.'
    - When file with altered header is scraped, scraper errors contains 'Bad
      date string length'.
    - When file with missing data is scraped, scraper errors contains
      'unexpected end of file'.
    - When well-formedness is checked, MIME type application/x-spss-por is
      supported with '', None or 'foo' as a version
    - When well-formedness is not checked, application/x-spss-por is not
      supported.
    - When well-formedness is checked, a made up MIME type is not supported.
"""
from __future__ import unicode_literals

import pytest

from file_scraper.defaults import UNAP, UNAV
from file_scraper.pspp.pspp_scraper import PsppScraper
from tests.common import parse_results

MIMETYPE = "application/x-spss-por"


@pytest.mark.parametrize(
    ["filename", "result_dict"],
    [
        ("valid__spss24-dot.por", {
            "purpose": "Test valid file that uses the newer standard (used by "
                       "e.g. SPSS 24) for DOT data type..",
            "stdout_part": "File conversion was succesful.",
            "stderr_part": ""}),
        ("valid__spss24-dates.por", {
            "purpose": "Test valid file that uses the newer standard (used by "
                       "e.g. SPSS 24) for DATE data types..",
            "stdout_part": "File conversion was succesful.",
            "stderr_part": ""}),
        ("invalid__pspp_header.por", {
            "purpose": "Test invalid file with PSPP header.",
            "stdout_part": "",
            "stderr_part": "File is not SPSS Portable format."}),
        ("valid__spss24-dates.por", {
            "purpose": "Test valid file with portable date formats.",
            "stdout_part": "File conversion was succesful.",
            "stderr_part": ""}),
        ("invalid__wrong_spss_format.sav", {
            "purpose": "Test wrong format.",
            "stdout_part": "",
            "stderr_part": "File is not SPSS Portable format."}),
        ("invalid__header_corrupted.por", {
            "purpose": "Test corrupted header.",
            "stdout_part": "",
            "stderr_part": "Bad date string length"}),
        ("invalid__truncated.por", {
            "purpose": "Test truncated file.",
            "stdout_part": "",
            "stderr_part": "unexpected end of file"})
    ]
)
def test_scraper(filename, result_dict, evaluate_scraper):
    """
    Test PSPP scraper.

    :filename: Test file name
    :result_dict: Result dict containing test purpose, and parts of
                  expected results of stdout and stderr
    """

    correct = parse_results(filename, MIMETYPE,
                            result_dict, True)
    if correct.well_formed:
        correct.streams[0]["version"] = UNAP
    else:
        correct.streams[0]["version"] = UNAV

    scraper = PsppScraper(filename=correct.filename,
                          mimetype="application/x-spss-por")
    scraper.scrape_file()

    evaluate_scraper(scraper, correct)


def test_is_supported():
    """Test is_supported method."""
    mime = MIMETYPE
    ver = ""
    assert PsppScraper.is_supported(mime, ver, True)
    assert PsppScraper.is_supported(mime, None, True)
    assert not PsppScraper.is_supported(mime, ver, False)
    assert PsppScraper.is_supported(mime, "foo", True)
    assert not PsppScraper.is_supported("foo", ver, True)
