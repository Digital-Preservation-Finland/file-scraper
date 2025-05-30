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
    - When using WarctoolsFullScraper:
        - For whiles where the reported content length is shorter than the
          actual content, scraper errors contains "warc errors at".

    - With well-formedness check, the following MIME types and versions are
      supported:
        - GzipWarctoolsScraper supports application/gzip with "", None or a
          made up string as a version.
        - WarctoolsScraper and WarctoolsFullScraper support
          application/warc with "", None or a made up string as a version.
    - Without well-formedness check, these MIME types are supported only in
      WarctoolsScraper.
    - None of these scrapers supports a made up MIME type.
"""
from pathlib import Path

import pytest

from file_scraper.defaults import UNAV
from file_scraper.warctools.warctools_scraper import (
    GzipWarctoolsScraper, WarctoolsFullScraper, WarctoolsScraper)
from tests.common import (parse_results, partial_message_included)


@pytest.mark.parametrize(
    ["filename", "result_dict"],
    [
        ("valid_1.0_.warc.gz", {
            "purpose": "Test valid warc file.",
            "stdout_part": "successfully",
            "stderr_part": ""}),
        ("invalid__empty.warc.gz", {
            "purpose": "Test empty warc file.",
            "stdout_part": "",
            "stderr_part": "Empty file."}),
        ("invalid__missing_data.warc.gz", {
            "purpose": "Test invalid warc gzip.",
            "stdout_part": "",
            "stderr_part": "Compressed file ended before the end-of-stream"
                           " marker was reached"}),
    ]
)
def test_gzip_scraper(filename, result_dict, evaluate_scraper):
    """
    Test scraper for gzip files.

    :filename: Test file name
    :result_dict: Result dict containing test purpose, and parts of
                  expected results of stdout and stderr
    """
    mime = "application/warc"
    classname = "WarctoolsFullScraper"
    correct = parse_results(filename, mime,
                            result_dict, True)
    scraper = GzipWarctoolsScraper(filename=correct.filename,
                                   mimetype="application/gzip")
    scraper.scrape_file()

    if not correct.well_formed and correct.streams[0]["version"] == UNAV:
        correct.update_mimetype("application/gzip")
        classname = "GzipWarctoolsScraper"

    if not correct.well_formed:
        assert not scraper.well_formed
        assert not scraper.streams
        assert partial_message_included(correct.stdout_part,
                                        scraper.messages())
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
    """
    Test scraper for warc files.

    :filename: Test file name
    :result_dict: Result dict containing test purpose, and parts of
                  expected results of stdout and stderr
    """
    correct = parse_results(filename, "application/warc",
                            result_dict, True)
    scraper = WarctoolsFullScraper(filename=correct.filename,
                                   mimetype="application/warc")
    scraper.scrape_file()

    if not correct.well_formed:
        assert not scraper.well_formed
        assert not scraper.streams
        assert partial_message_included(correct.stdout_part,
                                        scraper.messages())
        assert partial_message_included(correct.stderr_part, scraper.errors())
    else:
        evaluate_scraper(scraper, correct)


@pytest.mark.usefixtures("patch_shell_attributes_fx")
def test_warctools_returns_invalid_return_code():
    """Test that a correct error message is given
    when the tool gives an invalid return code"""
    mimetype = "application/warc"
    path = Path("tests/data", mimetype.replace("/", "_"))
    testfile = path / "valid_0.17.warc"

    scraper = WarctoolsFullScraper(filename=testfile,
                                   mimetype=mimetype)

    scraper.scrape_file()

    assert "Warctools returned invalid return code: -1\n" in scraper.errors()


@pytest.mark.parametrize(
    ["scraper_class", "mimetype", "version", "only_wellformed"],
    [(GzipWarctoolsScraper, "application/gzip", "", True),
     (WarctoolsFullScraper, "application/warc", "1.0", True),
     (WarctoolsScraper, "application/warc", "1.0", False)]
)
def test_is_supported(scraper_class, mimetype, version, only_wellformed):
    """Test is_supported method."""
    assert scraper_class.is_supported(mimetype, version, only_wellformed)
    assert scraper_class.is_supported(mimetype, None, only_wellformed)
    assert not scraper_class.is_supported(mimetype, version,
                                          not only_wellformed)
    assert scraper_class.is_supported(mimetype, "foo", only_wellformed)
    assert not scraper_class.is_supported("foo", version, only_wellformed)
