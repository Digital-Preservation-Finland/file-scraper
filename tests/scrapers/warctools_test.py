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
from tests.common import parse_results, force_correct_filetype


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
    scraper = GzipWarctoolsScraper(correct.filename, True, correct.params)
    scraper.scrape_file()

    if correct.version == "" or correct.mimetype == \
            "application/x-internet-archive":
        correct.version = None
        correct.streams[0]["version"] = "(:unav)"
    if not correct.well_formed and correct.version is None:
        correct.mimetype = "application/gzip"
        correct.streams[0]["mimetype"] = "application/gzip"
        classname = "GzipWarctoolsScraper"

    if not correct.well_formed:
        assert not scraper.well_formed
        assert not scraper.streams
        assert correct.stdout_part in scraper.messages()
        assert correct.stderr_part in scraper.errors()
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
    scraper = WarcWarctoolsScraper(correct.filename, True, correct.params)
    scraper.scrape_file()
    if correct.version == "":
        correct.version = None
    if correct.streams[0]["version"] == "":
        correct.streams[0]["version"] = None

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
    scraper = ArcWarctoolsScraper(correct.filename, True, correct.params)
    scraper.scrape_file()
    correct.streams[0]["version"] = "(:unav)"
    correct.version = None

    if not correct.well_formed:
        assert not scraper.well_formed
        assert not scraper.streams
        assert correct.stdout_part in scraper.messages()
        assert correct.stderr_part in scraper.errors()
    else:
        evaluate_scraper(scraper, correct)


def test_no_wellformed_gzip():
    """Test scraper without well-formed check."""
    scraper = GzipWarctoolsScraper(
        "tests/data/application_warc/valid_1.0_.warc.gz", False)
    scraper.scrape_file()
    assert "Skipping scraper" in scraper.messages()
    assert scraper.well_formed is None


def test_no_wellformed_warc():
    """Test scraper without well-formed check."""
    scraper = WarcWarctoolsScraper(
        "tests/data/application_warc/valid_1.0_.warc", False)
    scraper.scrape_file()
    assert "Skipping scraper" in scraper.messages()
    assert scraper.well_formed is None


def test_no_wellformed_arc():
    """Test scraper without well-formed check."""
    scraper = ArcWarctoolsScraper(
        "tests/data/application_x-internet-archive/valid_1.0_.arc", False)
    scraper.scrape_file()
    assert "Skipping scraper" in scraper.messages()
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


def run_filetype_test(filename, result_dict, filetype, scraper_class,
                      evaluate_scraper):
    """
    Runs scraper result evaluation for a scraper with forced MIME type/version

    :filename: Name of the file, not containing the tests/data/mime_type/ part
    :result_dict: Result dict to be given to Correct
    :filetype: A dict containing the forced, expected and real file types under
               the following keys:
                * given_mimetype: the forced MIME type
                * given_version: the forced version
                * expected_mimetype: the expected resulting MIME type
                * expected_version: the expected resulting version
                * correct_mimetype: the real MIME type of the file
    """
    correct = force_correct_filetype(filename, result_dict,
                                     filetype)

    if filetype["given_mimetype"]:
        mimetype_guess = filetype["given_mimetype"]
    else:
        mimetype_guess = filetype["correct_mimetype"]
    params = {"mimetype": filetype["given_mimetype"],
              "version": filetype["given_version"],
              "mimetype_guess": mimetype_guess}
    scraper = scraper_class(correct.filename, True, params)
    scraper.scrape_file()

    if "warc" in filename:
        classname = "WarcWarctoolsScraper"
    else:
        classname = "ArcWarctoolsScraper"
    evaluate_scraper(scraper, correct, exp_scraper_cls=classname)


@pytest.mark.parametrize(
    ["filename", "mimetype", "version", "version_result", "scraper_class"],
    [
        ("valid_1.0.warc", "application/warc", "1.0", "1.0",
         WarcWarctoolsScraper),
        ("valid_1.0_.warc.gz", "application/warc", "1.0", "1.0",
         GzipWarctoolsScraper),
        ("valid_1.0.arc", "application/x-internet-archive", "1.0", "(:unav)",
         ArcWarctoolsScraper),
        ("valid_1.0_.arc.gz", "application/x-internet-archive", "1.0",
         "(:unav)", GzipWarctoolsScraper),
    ]
)
def test_forced_filetype(filename, mimetype, version, version_result,
                         scraper_class, evaluate_scraper):
    """
    Tests the simple cases of file type forcing.

    Here, the following cases are tested for one file type scraped using each
    metadata model class supported by MagicScraper:
        - Force the scraper to use the correct MIME type and version, which
          should always result in the given MIME type and version and the file
          should be well-formed.
        - Force the scraper to use the correct MIME type, which should always
          result in the given MIME type and the version the metadata model
          would normally return.
        - Give forced version without MIME type, which should result in the
          scraper running normally and not affect its results or messages.
        - Force the scraper to use an unsupported MIME type, which should
          result in an error message being logged and the scraper reporting
          the file as not well-formed.
    """
    # pylint: disable=too-many-arguments
    result_dict = {"purpose": "Test forcing correct MIME type and version",
                   "stdout_part": "MIME type and version not scraped, using",
                   "stderr_part": ""}
    filetype_dict = {"given_mimetype": mimetype,
                     "given_version": version,
                     "expected_mimetype": mimetype,
                     "expected_version": version,
                     "correct_mimetype": mimetype}
    run_filetype_test(filename, result_dict, filetype_dict, scraper_class,
                      evaluate_scraper)

    result_dict = {"purpose": "Test forcing correct MIME type without version",
                   "stdout_part": "MIME type not scraped, using",
                   "stderr_part": ""}
    filetype_dict = {"given_mimetype": mimetype,
                     "given_version": None,
                     "expected_mimetype": mimetype,
                     "expected_version": version_result,
                     "correct_mimetype": mimetype}
    run_filetype_test(filename, result_dict, filetype_dict, scraper_class,
                      evaluate_scraper)

    result_dict = {"purpose": "Test forcing version only (no effect)",
                   "stdout_part": "File was analyzed successfully",
                   "stderr_part": ""}
    filetype_dict = {"given_mimetype": None,
                     "given_version": "99.9",
                     "expected_mimetype": mimetype,
                     "expected_version": version_result,
                     "correct_mimetype": mimetype}
    run_filetype_test(filename, result_dict, filetype_dict, scraper_class,
                      evaluate_scraper)

    result_dict = {"purpose": "Test forcing wrong MIME type",
                   "stdout_part": "MIME type not scraped, using",
                   "stderr_part": "is not supported"}
    filetype_dict = {"given_mimetype": "unsupported/mime",
                     "given_version": None,
                     "expected_mimetype": "unsupported/mime",
                     "expected_version": version_result,
                     "correct_mimetype": mimetype}
    run_filetype_test(filename, result_dict, filetype_dict, scraper_class,
                      evaluate_scraper)
