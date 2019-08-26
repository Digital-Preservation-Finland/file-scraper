"""
Test for pdf 1.7 ghostscript scraper.

This module tests that:
    - When full scraping is done for a valid pdf file, the following results
      are reported:
        - the file is well-formed
        - MIME type is application/pdf
        - scraper messages do not contain the word 'Error'
        - version is None
        - in streams, version is None
    - Forcing MIME type and/or version is possible.
    - Files containing JPEG2000 images are scraped correctly.
    - When full scraping is done for a file where the payload has been altered,
      or an XREF entry in XREF table has been removed, the results are similar
      but the file is not well-formed, scraper messages are not checked and
      scraper errors contain 'An error occurred while reading an XREF table.'
    - When well-formedness is not checked, scraper messages should contain
      'Skipping scraper' and well-formednes be reported as None
    - MIME type application/pdf with version 1.7 is reported as
      supported when full scraping is done
    - When full scraping is not done, application/pdf version 1.7 is reported
      as not supported
    - Supported MIME type with made up version is reported as not supported
    - Made up MIME type with supported version is reported as not supported
"""
from __future__ import unicode_literals

import pytest

from file_scraper.ghostscript.ghostscript_scraper import GhostscriptScraper
from tests.common import (parse_results, force_correct_filetype,
                          partial_message_included)


@pytest.mark.parametrize(
    ["filename", "result_dict"],
    [
        ("valid_X.pdf", {
            "purpose": "Test valid file.",
            "stdout_part": "Well-Formed and valid",
            "stderr_part": ""}),
        ("invalid_X_payload_altered.pdf", {
            "purpose": "Test payload altered file.",
            "stdout_part": "Error: Tf refers to an unknown resource name",
            "stderr_part": ""}),
        ("invalid_X_removed_xref.pdf", {
            "purpose": "Test xref change.",
            "stdout_part": "Error:  An error occurred while reading an XREF",
            "stderr_part": ""}),
    ]
)
def test_scraper_pdf(filename, result_dict, evaluate_scraper):
    """Test scraper."""
    for ver in ["1.7", "A-1a", "A-2b", "A-3b"]:
        filename = filename.replace("X", ver)
        correct = parse_results(filename, "application/pdf",
                                result_dict, True)
        scraper = GhostscriptScraper(correct.filename, True, correct.params)
        scraper.scrape_file()

        # Ghostscript cannot handle version or MIME type
        correct.version = "(:unav)"
        correct.streams[0]["version"] = "(:unav)"
        correct.mimetype = "(:unav)"
        correct.streams[0]["mimetype"] = "(:unav)"

        evaluate_scraper(scraper, correct, eval_output=False)

        if scraper.well_formed:
            assert not partial_message_included("Error", scraper.messages())
            assert not scraper.errors()
        else:
            assert partial_message_included(correct.stderr_part,
                                            scraper.errors())
            assert partial_message_included(correct.stdout_part,
                                            scraper.messages())


@pytest.mark.parametrize(
    ["filename", "result_dict", "filetype"],
    [
        ("valid_1.7.pdf", {
            "purpose": "Test not forcing anything.",
            "stdout_part": "Well-Formed and valid",
            "stderr_part": ""},
         {"given_mimetype": None, "given_version": None,
          "expected_mimetype": "(:unav)", "expected_version": "(:unav)",
          "correct_mimetype": "application/pdf"}),
        ("valid_1.7.pdf", {
            "purpose": "Test forcing incompatible MIME type.",
            "stdout_part": "MIME type not scraped",
            "stderr_part": "is not supported"},
         {"given_mimetype": "custom/mime", "given_version": None,
          "expected_mimetype": "custom/mime", "expected_version": "(:unav)",
          "correct_mimetype": "application/pdf"}),
        ("valid_1.7.pdf", {
            "purpose": "Test forcing incompatible MIME type and version.",
            "stdout_part": "MIME type and version not scraped",
            "stderr_part": "is not supported"},
         {"given_mimetype": "custom/mime", "given_version": "99.9",
          "expected_mimetype": "custom/mime", "expected_version": "99.9",
          "correct_mimetype": "application/pdf"}),
        ("valid_1.7.pdf", {
            "purpose": "Test forcing only version (no effect).",
            "stdout_part": "Well-Formed and valid",
            "stderr_part": ""},
         {"given_mimetype": None, "given_version": "99.9",
          "expected_mimetype": "(:unav)", "expected_version": "(:unav)",
          "correct_mimetype": "application/pdf"}),
        ("valid_1.7.pdf", {
            "purpose": "Test forcing correct MIME type and version",
            "stdout_part": "Well-Formed and valid",
            "stderr_part": ""},
         {"given_mimetype": "application/pdf", "given_version": "1.7",
          "expected_mimetype": "application/pdf", "expected_version": "1.7",
          "correct_mimetype": "application/pdf"}),
    ]
)
def test_forcing_filetype(filename, result_dict, filetype, evaluate_scraper):
    """Test forcing scraper to use a given MIME type and/or version."""
    correct = force_correct_filetype(filename, result_dict,
                                     filetype, "(:unav)")

    params = {"mimetype": filetype["given_mimetype"],
              "version": filetype["given_version"]}
    scraper = GhostscriptScraper(correct.filename, True, params)
    scraper.scrape_file()

    evaluate_scraper(scraper, correct)


def test_jpeg2000_inside_pdf(evaluate_scraper):
    """
    Test scraping a pdf file containing JPEG2000 image.

    Default Ghostscript installation on CentOS 7 does not support pdf files
    containing JPXDecode data. This test verifies that the installed version is
    recent enough.
    """
    filename = "valid_1.7_jpeg2000.pdf"
    mimetype = "application/pdf"
    result_dict = {"purpose": "Test pdf with JPEG2000 inside it.",
                   "stdout_part": "Well-formed and valid",
                   "stderr_part": ""}
    correct = parse_results(filename, mimetype, result_dict, True)

    scraper = GhostscriptScraper(correct.filename, True)
    scraper.scrape_file()

    # Ghostscript cannot handle version or MIME type
    correct.version = "(:unav)"
    correct.streams[0]["version"] = "(:unav)"
    correct.mimetype = "(:unav)"
    correct.streams[0]["mimetype"] = "(:unav)"

    evaluate_scraper(scraper, correct, eval_output=False)


def test_no_wellformed():
    """Test scraper without well-formed check."""
    scraper = GhostscriptScraper("tests/data/application_pdf/valid_1.4.pdf",
                                 False)
    scraper.scrape_file()
    assert partial_message_included("Skipping scraper", scraper.messages())
    assert scraper.well_formed is None


def test_is_supported():
    """Test is_supported method."""
    mime = "application/pdf"
    ver = "1.7"
    assert GhostscriptScraper.is_supported(mime, ver, True)
    assert GhostscriptScraper.is_supported(mime, None, True)
    assert not GhostscriptScraper.is_supported(mime, ver, False)
    assert not GhostscriptScraper.is_supported(mime, "foo", True)
    assert not GhostscriptScraper.is_supported("foo", ver, True)
