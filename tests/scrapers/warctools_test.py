"""
Test the file_scraper.scrapers.warctools module

This module tests that:
    - MIME type, version, streams and well-formedneess are scraped correctly
      using all scrapers.
        - For all well-formed files, scraper messages contain "successfully".
    - When using GzipWarctoolsScraper:
        - For empty files, scraper errors contains "Empty file."
        - For files with missing data, scraper errors contains "unpack
          requires a string argument of length 4".
    - When using WarcWarctoolsScraper:
        - For whiles where the reported content length is shorter than the
          actual content, scraper errors contains "warc errors at".
    - When using ArcWarctoolsScraper:
        - For files where a header field is missing, scraper errors contains
          "Exception: missing headers".
        - For files with missing data, scraper errors contains "unpack
          requires a string argument of length 4".

    - When using any of these scrapers without checking well-formedness,
      scraper messages contains "Skipping scraper" and well_formed is None.

    - With well-formedness check, the following MIME types and versions are
      supported:
        - GzipWarctoolsScraper supports application/gzip with "", None or a
          made up string as a version.
        - WarcWarctoolsScraper supports application/warc with "", None or a
          made up string as a version.
        - ArcWarctoolsScraper supports applivation/x-internet-archive with "",
          None or a made up string as a version
    - Without well-formedness check, these MIME types are not supported.
    - None of these scrapers supports a made up MIME type.
    - MIME type and/or version forcing works.
"""
from __future__ import unicode_literals

import pytest

from file_scraper.warctools.warctools_scraper import (ArcWarctoolsScraper,
                                                      GzipWarctoolsScraper,
                                                      WarcWarctoolsScraper)
from tests.common import (parse_results, partial_message_included)


@pytest.mark.parametrize(
    ["filename", "result_dict"],
    [
        ("valid_1.0_.warc.gz", {
            "purpose": "Test valid warc file.",
            "stdout_part": "successfully",
            "stderr_part": ""}),
        ("valid_1.0_.arc.gz", {
            "purpose": "Test valid arc file.",
            "stdout_part": "successfully",
            "stderr_part": ""}),
        ("invalid__empty.warc.gz", {
            "purpose": "Test empty warc file.",
            "stdout_part": "",
            "stderr_part": "Empty file."}),
        ("invalid__missing_data.warc.gz", {
            "purpose": "Test invalid warc gzip.",
            "stdout_part": "",
            "stderr_part": "unpack requires a string argument of length 4"}),
        ("invalid__missing_data.arc.gz", {
            "purpose": "Test invalid arc gzip.",
            "stdout_part": "",
            "stderr_part": "unpack requires a string argument of length 4"}),
        ("invalid__empty.arc.gz", {
            "purpose": "Test empty arc file.",
            "stdout_part": "",
            "stderr_part": "Empty file."})
    ]
)
def test_gzip_scraper(filename, result_dict, evaluate_scraper):
    """Test scraper."""
    if "warc" in filename:
        mime = "application/warc"
        classname = "WarcWarctoolsScraper"
    else:
        mime = "application/x-internet-archive"
        classname = "ArcWarctoolsScraper"
    correct = parse_results(filename, mime,
                            result_dict, True)
    scraper = GzipWarctoolsScraper(filename=correct.filename,
                                   mimetype="application/gzip")
    scraper.scrape_file()

    if correct.streams[0]["mimetype"] == "application/x-internet-archive":
        correct.streams[0]["version"] = "(:unav)"
    if not correct.well_formed and correct.streams[0]["version"] == "(:unav)":
        correct.streams[0]["mimetype"] = "application/gzip"
        classname = "GzipWarctoolsScraper"

    if not correct.well_formed:
        assert not scraper.well_formed
        assert not scraper.streams
        assert partial_message_included(correct.stdout_part, scraper.messages())
        assert partial_message_included(correct.stderr_part, scraper.errors())
    else:
        evaluate_scraper(scraper, correct, exp_scraper_cls=classname)


@pytest.mark.parametrize(
    ["filename", "result_dict"],
    [
        ("valid_0.17.warc", {
            "purpose": "Test valid file.",
            "stdout_part": "successfully",
            "stderr_part": ""}),
        ("valid_0.18.warc", {
            "purpose": "Test valid file.",
            "stdout_part": "successfully",
            "stderr_part": ""}),
        ("valid_1.0.warc", {
            "purpose": "Test valid file.",
            "stdout_part": "successfully",
            "stderr_part": ""}),
        ("invalid_0.17_too_short_content_length.warc", {
            "purpose": "Test short content length.",
            "stdout_part": "",
            "stderr_part": "warc errors at"}),
        ("invalid_0.18_too_short_content_length.warc", {
            "purpose": "Test short content length.",
            "stdout_part": "",
            "stderr_part": "warc errors at"}),
        ("invalid__empty.warc", {
            "purpose": "Test empty warc file.",
            "stdout_part": "",
            "stderr_part": "Empty file."}),
        ("invalid__empty.warc.gz", {
            "purpose": "Test empty gz file.",
            "stdout_part": "",
            "stderr_part": "Empty file."})
    ]
)
def test_warc_scraper(filename, result_dict, evaluate_scraper):
    """Test scraper."""
    correct = parse_results(filename, "application/warc",
                            result_dict, True)
    scraper = WarcWarctoolsScraper(filename=correct.filename,
                                   mimetype="application/warc")
    scraper.scrape_file()

    if not correct.well_formed:
        assert not scraper.well_formed
        assert not scraper.streams
        assert partial_message_included(correct.stdout_part, scraper.messages())
        assert partial_message_included(correct.stderr_part, scraper.errors())
    else:
        evaluate_scraper(scraper, correct)


@pytest.mark.parametrize(
    ["filename", "result_dict"],
    [
        ("valid_1.0.arc", {
            "purpose": "Test valid file.",
            "stdout_part": "successfully",
            "stderr_part": ""}),
        ("valid_1.0_.arc.gz", {
            "purpose": "Test valid file.",
            "stdout_part": "successfully",
            "stderr_part": ""}),
        ("invalid__empty.arc", {
            "purpose": "Test empty arc file.",
            "stdout_part": "",
            "stderr_part": "Empty file."}),
        ("invalid__empty.arc.gz", {
            "purpose": "Test empty gz file.",
            "stdout_part": "",
            "stderr_part": "Empty file."}),
        ("invalid_1.0_missing_field.arc", {
            "purpose": "Test missing header",
            "stdout_part": "",
            "stderr_part": "Exception: missing headers"}),
        ("invalid__missing_data.arc.gz", {
            "purpose": "Test missing data.",
            "stdout_part": "",
            "stderr_part": "unpack requires a string argument of length 4"})
    ]
)
def test_arc_scraper(filename, result_dict, evaluate_scraper):
    """Test scraper."""
    correct = parse_results(filename, "application/x-internet-archive",
                            result_dict, True)
    scraper = ArcWarctoolsScraper(
        filename=correct.filename,
        mimetype="application/x-internet-archive")
    scraper.scrape_file()
    correct.streams[0]["version"] = "(:unav)"

    if not correct.well_formed:
        assert not scraper.well_formed
        assert not scraper.streams
        assert partial_message_included(correct.stdout_part, scraper.messages())
        assert partial_message_included(correct.stderr_part, scraper.errors())
    else:
        evaluate_scraper(scraper, correct)


def test_no_wellformed_gzip():
    """Test scraper without well-formed check."""
    scraper = GzipWarctoolsScraper(
        filename="tests/data/application_warc/valid_1.0_.warc.gz",
        mimetype="application/warc", check_wellformed=False)
    scraper.scrape_file()
    assert partial_message_included("Skipping scraper", scraper.messages())
    assert scraper.well_formed is None


def test_no_wellformed_warc():
    """Test scraper without well-formed check."""
    scraper = WarcWarctoolsScraper(
        filename="tests/data/application_warc/valid_1.0_.warc",
        mimetype="application/warc", check_wellformed=False)
    scraper.scrape_file()
    assert partial_message_included("Skipping scraper", scraper.messages())
    assert scraper.well_formed is None


def test_no_wellformed_arc():
    """Test scraper without well-formed check."""
    scraper = ArcWarctoolsScraper(
        filename="tests/data/application_x-internet-archive/valid_1.0_.arc",
        mimetype="application/x-internet-archive", check_wellformed=False)
    scraper.scrape_file()
    assert partial_message_included("Skipping scraper", scraper.messages())
    assert scraper.well_formed is None


def test_gzip_is_supported():
    """Test is_supported method."""
    mime = "application/gzip"
    ver = ""
    assert GzipWarctoolsScraper.is_supported(mime, ver, True)
    assert GzipWarctoolsScraper.is_supported(mime, None, True)
    assert not GzipWarctoolsScraper.is_supported(mime, ver, False)
    assert GzipWarctoolsScraper.is_supported(mime, "foo", True)
    assert not GzipWarctoolsScraper.is_supported("foo", ver, True)


def test_warc_is_supported():
    """Test is_supported method."""
    mime = "application/warc"
    ver = ""
    assert WarcWarctoolsScraper.is_supported(mime, ver, True)
    assert WarcWarctoolsScraper.is_supported(mime, None, True)
    assert not WarcWarctoolsScraper.is_supported(mime, ver, False)
    assert WarcWarctoolsScraper.is_supported(mime, "foo", True)
    assert not WarcWarctoolsScraper.is_supported("foo", ver, True)


def test_arc_is_supported():
    """Test is_supported method."""
    mime = "application/x-internet-archive"
    ver = ""
    assert ArcWarctoolsScraper.is_supported(mime, ver, True)
    assert ArcWarctoolsScraper.is_supported(mime, None, True)
    assert not ArcWarctoolsScraper.is_supported(mime, ver, False)
    assert ArcWarctoolsScraper.is_supported(mime, "foo", True)
    assert not ArcWarctoolsScraper.is_supported("foo", ver, True)
