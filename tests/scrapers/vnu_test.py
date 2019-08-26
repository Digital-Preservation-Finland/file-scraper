"""
Tests for Vnu scraper.

This module tests that:
    - MIME type, version, streams and well-formedness are scraped correctly for
      html 5 files when well-formedness is checked.
    - For well-formed file, scraper messages contain "valid_5.0.html".
    - For file without doctype, scraper errors contain  "Start tag seen
      without seeing a doctype first."
    - For file with illegal tags in it, scraper errors contain "not allowed as
      child of element".
    - For empty file, scraper errors contain "End of file seen without seeing
      a doctype first".
    - When well-formedness is not checked, scraper messages contain "Skipping
      scraper" and well_formed is None.
    - When well-formedness is checked, MIME type text/html versions 5.0 and
      None are supported. When well-formedness is not checked, this combination
      is not supported.
    - A made up MIME type or version is not supported.
    - MIME type and/or version forcing works.
"""
from __future__ import unicode_literals

import pytest
import six

from file_scraper.vnu.vnu_scraper import VnuScraper
from tests.common import (parse_results, force_correct_filetype,
                          partial_message_included)

MIMETYPE = "text/html"


@pytest.mark.parametrize(
    ["filename", "result_dict"],
    [
        ("valid_5.0.html", {
            "purpose": "Test valid file.",
            "stdout_part": "valid_5.0.html",
            "stderr_part": ""}),
        ("invalid_5.0_nodoctype.html", {
            "purpose": "Test valid file.",
            "stdout_part": "",
            "stderr_part": "Start tag seen without seeing a doctype first."}),
        ("invalid_5.0_illegal_tags.html", {
            "purpose": "Test valid file.",
            "stdout_part": "",
            "stderr_part": "not allowed as child of element"}),
        ("invalid__empty.html", {
            "purpose": "Test valid file.",
            "stdout_part": "",
            "stderr_part": "End of file seen without seeing a doctype first"}),
    ]
)
def test_scraper(filename, result_dict, evaluate_scraper):
    """Test scraper."""
    correct = parse_results(filename, MIMETYPE,
                            result_dict, True)
    scraper = VnuScraper(correct.filename, True, correct.params)
    scraper.scrape_file()
    correct.version = "5.0"
    correct.streams[0]["version"] = "5.0"

    if not correct.well_formed:
        assert not scraper.well_formed
        assert not scraper.streams
        assert partial_message_included(correct.stdout_part, scraper.messages())
        assert partial_message_included(correct.stderr_part, scraper.errors())
    else:
        evaluate_scraper(scraper, correct)


def test_no_wellformed():
    """Test scraper without well-formed check."""
    scraper = VnuScraper("tests/data/text_html/valid_5.0.html", False)
    scraper.scrape_file()
    assert partial_message_included("Skipping scraper", scraper.messages())
    assert scraper.well_formed is None


def test_is_supported():
    """Test is_supported method."""
    mime = MIMETYPE
    ver = "5.0"
    assert VnuScraper.is_supported(mime, ver, True)
    assert VnuScraper.is_supported(mime, None, True)
    assert not VnuScraper.is_supported(mime, ver, False)
    assert not VnuScraper.is_supported(mime, "foo", True)
    assert not VnuScraper.is_supported("foo", ver, True)


@pytest.mark.parametrize(
    ["result_dict", "filetype"],
    [
        ({"purpose": "Test forcing correct MIME type and version",
          "stdout_part": "MIME type and version not scraped, using",
          "stderr_part": ""},
         {"given_mimetype": "text/html",
          "given_version": "5.0",
          "expected_mimetype": "text/html",
          "expected_version": "5.0"}),
        ({"purpose": "Test forcing correct MIME type",
          "stdout_part": "MIME type not scraped, using",
          "stderr_part": ""},
         {"given_mimetype": "text/html",
          "given_version": None,
          "expected_mimetype": "text/html",
          "expected_version": "5.0"}),
        ({"purpose": "Test forcing version only (no effect)",
          "stdout_part": "",
          "stderr_part": ""},
         {"given_mimetype": None, "given_version": "99.9",
          "expected_mimetype": "text/html", "expected_version": "5.0"}),
        ({"purpose": "Test forcing wrong MIME type",
          "stdout_part": "MIME type not scraped, using",
          "stderr_part": "is not supported"},
         {"given_mimetype": "unsupported/mime", "given_version": None,
          "expected_mimetype": "unsupported/mime",
          "expected_version": "5.0"})
    ]
)
def test_forced_filetype(result_dict, filetype, evaluate_scraper):
    """
    Test using user-supplied MIME-types and versions.
    """
    filetype[six.text_type("correct_mimetype")] = "text/html"
    correct = force_correct_filetype("valid_5.0.html", result_dict,
                                     filetype)

    params = {"mimetype": filetype["given_mimetype"],
              "version": filetype["given_version"]}
    scraper = VnuScraper(correct.filename, True, params)
    scraper.scrape_file()

    evaluate_scraper(scraper, correct)
