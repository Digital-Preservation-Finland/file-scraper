"""
Test the file_scraper.warctools.warctools_extractor module

This module tests that:
    - MIME type, version, streams and well-formedneess are scraped correctly
      using all extractors.
        - For all well-formed files, extractor messages contain "successfully".
    - When using GzipWarctoolsExtractor:
        - For empty files, extractor errors contains "Empty file."
        - For files with missing data, extractor errors contains "unpack
          requires a string argument of length 4".
    - When using WarctoolsFullExtractor:
        - For whiles where the reported content length is shorter than the
          actual content, extractor errors contains "warc errors at".

    - With well-formedness check, the following MIME types and versions are
      supported:
        - GzipWarctoolsExtractor supports application/gzip with "", None or a
          made up string as a version.
        - WarctoolsExtractor and WarctoolsFullExtractor support
          application/warc with "", None or a made up string as a version.
    - Without well-formedness check, these MIME types are supported only in
      WarctoolsExtractor.
    - None of these extractors supports a made up MIME type.
"""
from pathlib import Path

import pytest

from file_scraper.defaults import UNAV
from file_scraper.warctools.warctools_extractor import (
    GzipWarctoolsExtractor, WarctoolsFullExtractor, WarctoolsExtractor)
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
def test_gzip_extractor(filename, result_dict, evaluate_extractor):
    """
    Test extractor for gzip files.

    :filename: Test file name
    :result_dict: Result dict containing test purpose, and parts of
                  expected results of stdout and stderr
    """
    mime = "application/warc"
    classname = "WarctoolsFullExtractor"
    correct = parse_results(filename, mime,
                            result_dict, True)
    extractor = GzipWarctoolsExtractor(filename=correct.filename,
                                     mimetype="application/gzip")
    extractor.scrape_file()

    if not correct.well_formed and correct.streams[0]["version"] == UNAV:
        correct.update_mimetype("application/gzip")
        classname = "GzipWarctoolsExtractor"

    if not correct.well_formed:
        assert not extractor.well_formed
        assert not extractor.streams
        assert partial_message_included(correct.stdout_part,
                                        extractor.messages())
        assert partial_message_included(correct.stderr_part, extractor.errors())
    else:
        evaluate_extractor(extractor, correct, exp_extractor_cls=classname)


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
def test_warc_extractor(filename, result_dict, evaluate_extractor):
    """
    Test extractor for warc files.

    :filename: Test file name
    :result_dict: Result dict containing test purpose, and parts of
                  expected results of stdout and stderr
    """
    correct = parse_results(filename, "application/warc",
                            result_dict, True)
    extractor = WarctoolsFullExtractor(filename=correct.filename,
                                     mimetype="application/warc")
    extractor.scrape_file()

    if not correct.well_formed:
        assert not extractor.well_formed
        assert not extractor.streams
        assert partial_message_included(correct.stdout_part,
                                        extractor.messages())
        assert partial_message_included(correct.stderr_part, extractor.errors())
    else:
        evaluate_extractor(extractor, correct)


@pytest.mark.usefixtures("patch_shell_attributes_fx")
def test_warctools_returns_invalid_return_code():
    """Test that a correct error message is given
    when the tool gives an invalid return code"""
    mimetype = "application/warc"
    path = Path("tests/data", mimetype.replace("/", "_"))
    testfile = path / "valid_0.17.warc"

    extractor = WarctoolsFullExtractor(filename=testfile,
                                     mimetype=mimetype)

    extractor.scrape_file()

    assert "Warctools returned invalid return code: -1\n" in extractor.errors()


@pytest.mark.parametrize(
    ["extractor_class", "mimetype", "version", "only_wellformed"],
    [(GzipWarctoolsExtractor, "application/gzip", "", True),
     (WarctoolsFullExtractor, "application/warc", "1.0", True),
     (WarctoolsExtractor, "application/warc", "1.0", False)]
)
def test_is_supported(extractor_class, mimetype, version, only_wellformed):
    """Test is_supported method."""
    assert extractor_class.is_supported(mimetype, version, only_wellformed)
    assert extractor_class.is_supported(mimetype, None, only_wellformed)
    assert not extractor_class.is_supported(mimetype, version,
                                          not only_wellformed)
    assert extractor_class.is_supported(mimetype, "foo", only_wellformed)
    assert not extractor_class.is_supported("foo", version, only_wellformed)
