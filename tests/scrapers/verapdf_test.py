"""
Tests for VeraPDF scraper for PDF/A files.

This module tests that:
    - For pdf versions A-1a, A-2b and A-3b, MIME type, version, streams and
      well-formedness are scraped correctly. This is tested using one
      well-formed file and two erroneous ones (one with altered payload and
      one in which a xref entry has been removed) for each version.
    - For well-formed files, scraper messages contain "PDF file is compliant
      with Validation Profile requirements".
    - For the files with altered payload, scraper errors contain "can not
      locate xref table".
    - For the files with removed xref entry, scraper errors contain "In a
      cross reference subsection header".
    - For files that are valid PDF 1.7 or 1.4 but not valid PDF/A, MIME type,
      version and streams are scraped correctly but they are reported as
      not well-formed.
    - When well-formedness is not checked, scraper messages contain "Skipping
      scraper" and well_formed is None.
    - The scraper supports MIME type application/pdf with versions A-1b
      when well-formedness is checked, but does not support them when
      well-formedness is not checked. The scraper also does not support made
      up MIME types or versions.
    - Versions A-1a, A-1b, A-2a, A-2b, A-2u, A-3a, A-3b and A-3u are recorded
      in dict returned by get_important() function when scraper messages
      contain "Success", but when scraper errors contain "Error", the dict is
      empty.
    - MIME type and/or version forcing works.
"""
from __future__ import unicode_literals

import pytest
import six

from file_scraper.verapdf.verapdf_scraper import VerapdfScraper
from tests.common import parse_results, force_correct_filetype

MIMETYPE = "application/pdf"


@pytest.mark.parametrize(
    ["filename", "result_dict"],
    [
        ("valid_X.pdf", {
            "purpose": "Test valid file.",
            "stdout_part": "PDF file is compliant with Validation Profile "
                           "requirements.",
            "stderr_part": ""}),
        ("invalid_X_payload_altered.pdf", {
            "purpose": "Test payload altered file.",
            "stdout_part": "",
            "stderr_part": "can not locate xref table"}),
        ("invalid_X_removed_xref.pdf", {
            "purpose": "Test xref change.",
            "stdout_part": "",
            "stderr_part": "In a cross reference subsection header"}),
    ]
)
def test_scraper(filename, result_dict, evaluate_scraper):
    """Test scraper with PDF/A."""
    for ver in ["A-1a", "A-2b", "A-3b"]:
        filename = filename.replace("X", ver)
        correct = parse_results(filename, MIMETYPE,
                                result_dict, True)
        scraper = VerapdfScraper(correct.filename, True, correct.params)
        scraper.scrape_file()

        if not correct.well_formed:
            assert not scraper.well_formed
            assert not scraper.streams
            assert correct.stdout_part in scraper.messages()
            assert correct.stderr_part in scraper.errors()
        else:
            evaluate_scraper(scraper, correct)


@pytest.mark.parametrize(
    ["filename", "result_dict"],
    [
        ("valid_1.7.pdf", {
            "purpose": "Test valid PDF 1.7, but not valid PDF/A.",
            "inverse": True,
            "stdout_part": "",
            "stderr_part": "is not compliant with Validation Profile"}),
        ("valid_1.4.pdf", {
            "purpose": "Test valid PDF 1.4, but not valid PDF/A.",
            "inverse": True,
            "stdout_part": "",
            "stderr_part": "is not compliant with Validation Profile"}),
    ]
)
def test_scraper_invalid_pdfa(filename, result_dict, evaluate_scraper):
    """Test scraper with files that are not valid PDF/A."""
    correct = parse_results(filename, MIMETYPE,
                            result_dict, True)
    scraper = VerapdfScraper(correct.filename, True, correct.params)
    scraper.scrape_file()

    if not correct.well_formed:
        assert not scraper.well_formed
        assert not scraper.streams
        assert correct.stdout_part in scraper.messages()
        assert correct.stderr_part in scraper.errors()
    else:
        evaluate_scraper(scraper, correct)


def test_no_wellformed():
    """Test scraper without well-formed check."""
    scraper = VerapdfScraper("tests/data/application_pdf/valid_A-1a.pdf",
                             False)
    scraper.scrape_file()
    assert "Skipping scraper" in scraper.messages()
    assert scraper.well_formed is None


def test_is_supported():
    """Test is_supported method."""
    mime = MIMETYPE
    ver = "A-1b"
    assert VerapdfScraper.is_supported(mime, ver, True)
    assert VerapdfScraper.is_supported(mime, None, True)
    assert not VerapdfScraper.is_supported(mime, ver, False)
    assert not VerapdfScraper.is_supported(mime, "foo", True)
    assert not VerapdfScraper.is_supported("foo", ver, True)


@pytest.mark.parametrize(
    ["result_dict", "filetype"],
    [
        ({"purpose": "Test forcing correct MIME type and version",
          "stdout_part": "MIME type and version not scraped, using",
          "stderr_part": ""},
         {"given_mimetype": "application/pdf",
          "given_version": "A-1a",
          "expected_mimetype": "application/pdf",
          "expected_version": "A-1a"}),
        ({"purpose": "Test forcing correct MIME type",
          "stdout_part": "MIME type not scraped, using",
          "stderr_part": ""},
         {"given_mimetype": "application/pdf",
          "given_version": None,
          "expected_mimetype": "application/pdf",
          "expected_version": "A-1a"}),
        ({"purpose": "Test forcing correct MIME type wiht supported but "
                     "wrong version",
          "stdout_part": "MIME type and version not scraped, using",
          "stderr_part": ""},
         {"given_mimetype": "application/pdf",
          "given_version": "A-2a",
          "expected_mimetype": "application/pdf",
          "expected_version": "A-2a"}),
        ({"purpose": "Test forcing version only (no effect)",
          "stdout_part": "",
          "stderr_part": ""},
         {"given_mimetype": None, "given_version": "A-1a",
          "expected_mimetype": "application/pdf", "expected_version": "A-1a"}),
        ({"purpose": "Test forcing wrong MIME type",
          "stdout_part": "MIME type not scraped, using",
          "stderr_part": "is not supported"},
         {"given_mimetype": "unsupported/mime", "given_version": None,
          "expected_mimetype": "unsupported/mime",
          "expected_version": "A-1a"})
    ]
)
def test_forced_filetype(result_dict, filetype, evaluate_scraper):
    """
    Test using user-supplied MIME-types and versions.
    """
    filetype[six.text_type("correct_mimetype")] = "application/pdf"
    correct = force_correct_filetype("valid_A-1a.pdf", result_dict,
                                     filetype)

    params = {"mimetype": filetype["given_mimetype"],
              "version": filetype["given_version"]}
    scraper = VerapdfScraper(correct.filename, True, params)
    scraper.scrape_file()

    evaluate_scraper(scraper, correct)
