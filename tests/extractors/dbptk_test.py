"""
Tests for DBTK extractor.

This module tests that:
    - MIME type, version, streams and well-formedness are scraped
      correctly for SIARD files.
    - For well-formed file, extractor messages contain "SIARD is valid".
    - For files that do not conform to SIARD specifications, extractor
      errors contain "SIARD is not valid"
    - For file with unupported version, extractor errors contain "ERROR
      SIARD validator".
    - When well-formedness is checked, MIME type application/x-siard
      withh versions "2.1.1" or "2.2" are supported.
    - A made up MIME type or version is not supported.
"""
from pathlib import Path

import pytest

from file_scraper.defaults import UNAV
from file_scraper.dbptk.dbptk_extractor import DbptkExtractor
from tests.common import (parse_results, partial_message_included)

MIMETYPE = "application/x-siard"


@pytest.mark.parametrize(
    ["filename", "result_dict"],
    [
        ("valid_2.1.1.siard", {
            "purpose": "Test valid file.",
            "stdout_part": "Validation process finished the SIARD is valid.",
            "stderr_part": ""}),
        ("invalid_2.1.1_schema_errors.siard", {
            "purpose": "Test invalid file with invalid internal structure.",
            "stdout_part": "",
            "stderr_part": (
                "Validation process finished the SIARD is not valid.")}),
        ("invalid_2.0_invalid_version.siard", {
            "purpose": "Test unsupported version.",
            "stdout_part": "",
            "stderr_part": "ERROR SIARD validator"}),
        ("invalid_2.1.1_invalid_extension.zip", {
            "purpose": "Test invalid file with wrong file extension.",
            "stdout_part": "",
            "stderr_part": (
                "Validation process finished the SIARD is not valid.")}),
    ]
)
def test_extractor(filename, result_dict, evaluate_extractor):
    """
    Test DBPTK extractor.

    :filename: Test file name
    :result_dict: Result dict containing test purpose, and parts of
                  expected results of stdout and stderr
    """
    correct = parse_results(filename, MIMETYPE,
                            result_dict, True)
    correct.streams[0]["version"] = UNAV
    extractor = DbptkExtractor(filename=correct.filename, mimetype=MIMETYPE)
    extractor.extract()

    if not correct.well_formed:
        assert not extractor.well_formed
        assert partial_message_included(correct.stdout_part,
                                        extractor.messages())
        assert partial_message_included(correct.stderr_part,
                                        extractor.errors())
    else:
        evaluate_extractor(extractor, correct)


def test_is_supported():
    """Test is_supported method."""
    mime = MIMETYPE
    versions = ["2.1.1", "2.2"]

    assert DbptkExtractor.is_supported(mime, None, True)
    assert not DbptkExtractor.is_supported(mime, "foo", True)
    for ver in versions:
        assert DbptkExtractor.is_supported(mime, ver, True)
        assert not DbptkExtractor.is_supported(mime, ver, False)
        assert not DbptkExtractor.is_supported("foo", ver, True)


def test_tools_not_empty():
    """Test that dbptk extractor has exactly one dependency"""
    extractor = DbptkExtractor(filename=Path("valid_2.1.1.siard"), mimetype=MIMETYPE)
    assert len(extractor.tools()) == 1


def test_tools_returns_version():
    """Test thatdbptk extractor tools
    returns a somewhat valid version"""
    extractor = DbptkExtractor(filename=Path("invalid_2.1.1_schema_errors.siard"),
                             mimetype=MIMETYPE)

    assert extractor.tools()["DBPTK Developer"]["version"] not in (UNAV, None)
