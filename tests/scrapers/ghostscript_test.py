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
import pytest
from tests.common import parse_results
from file_scraper.ghostscript.ghostscript_scraper import GhostscriptScraper


@pytest.mark.parametrize(
    ["filename", "result_dict"],
    [
        ("valid_X.pdf", {
            "purpose": "Test valid file.",
            "stdout_part": "Well-Formed and valid",
            "stderr_part": ""}),
        ("invalid_X_payload_altered.pdf", {
            "purpose": "Test payload altered file.",
            "stdout_part": "An error occurred while reading an XREF table.",
            "stderr_part": ""}),
        ("invalid_X_removed_xref.pdf", {
            "purpose": "Test xref change.",
            "stdout_part": "An error occurred while reading an XREF table.",
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
            assert "Error" not in scraper.messages()
        else:
            assert correct.stdout_part in scraper.messages()
        assert correct.stderr_part in scraper.errors()


def test_jpeg2000_inside_pdf(evaluate_scraper):
    """
    Test scraping a pdf file containing JPEG2000 image.

    Default Ghostscript installation on CentOS 7 does not support pdf files
    containing JPXDecode data. This test verifies that the installed version is
    recent enough.
    """
    filename = "valid_1.7-jpeg2000.pdf"
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
    assert "Skipping scraper" in scraper.messages()
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
