"""
Test for Ghostscript scraper.

This module tests that:
    - The following results are reported:
        - the file is well-formed
        - MIME type and version are '(:unav)'
        - scraper messages do not contain the word 'Error'
    - Files containing JPEG2000 images are scraped correctly.
    - When scraping is done for a file where the payload has been altered,
      or an XREF entry in XREF table has been removed, the results are similar
      but the file is not well-formed, scraper messages are not checked and
      scraper errors contain 'An error occurred while reading an XREF table.'
    - MIME type application/pdf with version 1.7 is reported as
      supported when full scraping is done
    - When full scraping is not done, application/pdf version 1.7 is reported
      as not supported
    - Supported MIME type with made up version is reported as not supported
    - Made up MIME type with supported version is reported as not supported
"""
from __future__ import unicode_literals
import os

import pytest

from file_scraper.defaults import UNAV
from file_scraper.ghostscript.ghostscript_scraper import GhostscriptScraper
from tests.common import (parse_results, partial_message_included)


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
    """
    Test Ghostscript scraper.

    :filename: Test filename. Character X is replaced with versions 1.7,
               A-1a, A-2b, and A-3b. All of these files must be found.
    :result_dict: Result dict containing the test purpose, and parts of
                  expected results of stdout and stderr
    """
    for ver in ["1.7", "A-1a", "A-2b", "A-3b"]:
        filename = filename.replace("X", ver)
        correct = parse_results(filename, "application/pdf",
                                result_dict, True)
        scraper = GhostscriptScraper(filename=correct.filename,
                                     mimetype="application/pdf")
        scraper.scrape_file()

        # Ghostscript cannot handle version or MIME type
        correct.streams[0]["version"] = UNAV
        correct.streams[0]["mimetype"] = UNAV

        evaluate_scraper(scraper, correct, eval_output=False)

        if scraper.well_formed:
            assert not partial_message_included("Error", scraper.messages())
            assert not scraper.errors()
        else:
            assert partial_message_included(correct.stderr_part,
                                            scraper.errors())
            assert partial_message_included(correct.stdout_part,
                                            scraper.messages())


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

    scraper = GhostscriptScraper(filename=correct.filename, mimetype=mimetype)
    scraper.scrape_file()

    # Ghostscript cannot handle version or MIME type
    correct.streams[0]["version"] = UNAV
    correct.streams[0]["mimetype"] = UNAV

    evaluate_scraper(scraper, correct, eval_output=False)


@pytest.mark.usefixtures("patch_shell_attributes_fx")
def test_ghostscript_returns_invalid_return_code():
    """Test that a correct error message is given
    when the tool gives an invalid return code"""
    mimetype = "application/pdf"
    path = os.path.join("tests/data", mimetype.replace("/", "_"))
    testfile = os.path.join(path, "valid_X.pdf")

    scraper = GhostscriptScraper(filename=testfile,
                          mimetype=mimetype)

    scraper.scrape_file()

    assert "Ghostscript returned invalid return code: -1\n" in scraper.errors()


def test_is_supported():
    """Test is_supported method."""
    mime = "application/pdf"
    ver = "1.7"
    assert GhostscriptScraper.is_supported(mime, ver, True)
    assert GhostscriptScraper.is_supported(mime, None, True)
    assert not GhostscriptScraper.is_supported(mime, ver, False)
    assert not GhostscriptScraper.is_supported(mime, "foo", True)
    assert not GhostscriptScraper.is_supported("foo", ver, True)
