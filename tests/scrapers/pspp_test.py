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
    - When well-formedness is not checked, scraper messages contains 'Skipping
      scraper' and well_formed is None.
    - When well-formedness is checked, MIME type application/x-spss-por is
      supported with '', None or 'foo' as a version
    - When well-formedness is not checked, application/x-spss-por is not
      supported.
    - When well-formedness is checked, a made up MIME type is not supported.
    - MIME type and/or version forcing works.
"""
from __future__ import unicode_literals

import pytest
import six

from file_scraper.pspp.pspp_scraper import PsppScraper
from tests.common import (parse_results, force_correct_filetype,
                          partial_message_included)

MIMETYPE = "application/x-spss-por"


@pytest.mark.parametrize(
    ["filename", "result_dict"],
    [
        ("valid.por", {
            "purpose": "Test valid file.",
            "stdout_part": "File conversion was succesful.",
            "stderr_part": ""}),
        ("valid__spss24-dot.por", {
            "purpose": "Test valid file that uses the newer standard (used by "
                       "e.g. SPSS 24) for DOT data type..",
            "stdout_part": "File conversion was succesful.",
            "stderr_part": ""}),
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
            "stderr_part": "unexpected end of file"}),
        ("invalid__variable_types.por", {
            "purpose": "Test invalid file with bad portable date type.",
            "stdout_part": "",
            "stderr_part": "invalid__variable_types.por at offset 0x253: DATE:"
                           " Bad format specifier byte (282).  Variable "})
    ]
)
def test_scraper(filename, result_dict, evaluate_scraper):
    """Test scraper."""

    correct = parse_results(filename, MIMETYPE,
                            result_dict, True)
    scraper = PsppScraper(correct.filename, True, correct.params)
    scraper.scrape_file()

    correct.streams[0]["mimetype"] = "(:unav)"

    evaluate_scraper(scraper, correct)


def test_no_wellformed():
    """Test scraper without well-formed check."""
    scraper = PsppScraper("tests/data/application_x-spss-por/valid.por", False)
    scraper.scrape_file()
    assert partial_message_included("Skipping scraper", scraper.messages())
    assert scraper.well_formed is None


def test_is_supported():
    """Test is_supported method."""
    mime = MIMETYPE
    ver = ""
    assert PsppScraper.is_supported(mime, ver, True)
    assert PsppScraper.is_supported(mime, None, True)
    assert not PsppScraper.is_supported(mime, ver, False)
    assert PsppScraper.is_supported(mime, "foo", True)
    assert not PsppScraper.is_supported("foo", ver, True)


@pytest.mark.parametrize(
    ["result_dict", "filetype"],
    [
        ({"purpose": "Test forcing correct MIME type and version",
          "stdout_part": "MIME type and version not scraped, using",
          "stderr_part": ""},
         {"given_mimetype": "application/x-spss-por",
          "given_version": "(:unav)",
          "expected_mimetype": "application/x-spss-por",
          "expected_version": "(:unav)"}),
        ({"purpose": "Test forcing correct MIME type",
          "stdout_part": "MIME type not scraped, using",
          "stderr_part": ""},
         {"given_mimetype": "application/x-spss-por",
          "given_version": None,
          "expected_mimetype": "application/x-spss-por",
          "expected_version": "(:unav)"}),
        ({"purpose": "Test forcing version only (no effect)",
          "stdout_part": "",
          "stderr_part": ""},
         {"given_mimetype": None, "given_version": "(:unav)",
          "expected_mimetype": "(:unav)", "expected_version": "(:unav)"}),
        ({"purpose": "Test forcing wrong MIME type",
          "stdout_part": "MIME type not scraped, using",
          "stderr_part": "is not supported"},
         {"given_mimetype": "unsupported/mime", "given_version": None,
          "expected_mimetype": "unsupported/mime",
          "expected_version": "(:unav)"})
    ]
)
def test_forced_filetype(result_dict, filetype, evaluate_scraper):
    """
    Test using user-supplied MIME-types and versions.
    """
    filetype[six.text_type("correct_mimetype")] = "application/x-spss-por"
    correct = force_correct_filetype("valid.por", result_dict,
                                     filetype, ["(:unav)"])

    params = {"mimetype": filetype["given_mimetype"],
              "version": filetype["given_version"]}
    scraper = PsppScraper(correct.filename, True, params)
    scraper.scrape_file()

    evaluate_scraper(scraper, correct)
