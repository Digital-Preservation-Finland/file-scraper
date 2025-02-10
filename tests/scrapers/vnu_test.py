"""
Tests for Vnu scraper.

This module tests that:
    - MIME type, version, streams and well-formedness are scraped correctly for
      html 5 files.
    - For well-formed file, scraper messages contain "valid_5.html".
    - For file without doctype, scraper errors contain  "Start tag seen
      without seeing a doctype first."
    - For file with illegal tags in it, scraper errors contain "not allowed as
      child of element".
    - For empty file, scraper errors contain "End of file seen without seeing
      a doctype first".
    - When well-formedness is checked, MIME type text/html versions 5 and
      None are supported. When well-formedness is not checked, this combination
      is not supported.
    - A made up MIME type or version is not supported.
"""
import os

import pytest

from file_scraper.vnu.vnu_scraper import VnuScraper
from tests.common import (parse_results, partial_message_included)

MIMETYPE = "text/html"


@pytest.mark.parametrize(
    ["filename", "result_dict"],
    [
        ("valid_5.html", {
            "purpose": "Test valid file.",
            "stdout_part": "valid_5.html",
            "stderr_part": ""}),
        ("invalid_5_nodoctype.html", {
            "purpose": "Test valid file.",
            "stdout_part": "",
            "stderr_part": "Start tag seen without seeing a doctype first."}),
        ("invalid_5_illegal_tags.html", {
            "purpose": "Test valid file.",
            "stdout_part": "",
            "stderr_part": "not allowed as child of element"}),
        ("invalid__empty.html", {
            "purpose": "Test valid file.",
            "stdout_part": "",
            "stderr_part": "End of file seen without seeing a doctype first"}),
        ("valid_5_language_warning.html", {
            "purpose": "Test valid file.",
            "stdout_part": "valid_5_language_warning.html",
            "stderr_part": ""}),
        ("valid_5_unicode_normalization_warning.html", {
            "purpose": "Test that not using unicode normalization form C is "
                       "not an error.",
            "stdout_part": "valid_5_unicode_normalization_warning.html",
            "stderr_part": ""}),
    ]
)
def test_scraper(filename, result_dict, evaluate_scraper):
    """
    Test vnu scraper.

    :filename: Test file name
    :result_dict: Result dict containing test purpose, and parts of
                  expected results of stdout and stderr
    """
    correct = parse_results(filename, MIMETYPE,
                            result_dict, True)
    scraper = VnuScraper(filename=correct.filename, mimetype=MIMETYPE)
    scraper.scrape_file()

    if not correct.well_formed:
        assert not scraper.well_formed
        assert not scraper.streams
        assert partial_message_included(correct.stdout_part,
                                        scraper.messages())
        assert partial_message_included(correct.stderr_part,
                                        scraper.errors())
    else:
        evaluate_scraper(scraper, correct)


@pytest.mark.usefixtures("patch_shell_attributes_fx")
def test_vnu_returns_invalid_return_code():
    """Test that a correct error message is given
    when the tool gives an invalid return code"""
    path = os.path.join("tests/data", MIMETYPE.replace("/", "_"))
    testfile = os.path.join(path, "valid_5.html")

    scraper = VnuScraper(filename=testfile,
                         mimetype=MIMETYPE)

    scraper.scrape_file()

    assert "Vnu returned invalid return code: -1\n" in scraper.errors()


def test_is_supported():
    """Test is_supported method."""
    mime = MIMETYPE
    ver = "5"
    assert VnuScraper.is_supported(mime, ver, True)
    assert VnuScraper.is_supported(mime, None, True)
    assert not VnuScraper.is_supported(mime, ver, False)
    assert not VnuScraper.is_supported(mime, "foo", True)
    assert not VnuScraper.is_supported("foo", ver, True)
