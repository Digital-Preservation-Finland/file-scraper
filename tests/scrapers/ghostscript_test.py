"""
Test for Ghostscript extractor.

This module tests that:
    - The following results are reported:
        - the file is well-formed
        - MIME type and version are '(:unav)'
        - extractor messages do not contain the word 'Error'
    - Files containing JPEG2000 images are scraped correctly.
    - When scraping is done for a file where the payload has been altered,
      or an XREF entry in XREF table has been removed, the results are similar
      but the file is not well-formed, extractor messages are not checked and
      extractor errors contain 'An error occurred while reading an XREF table.'
    - MIME type application/pdf with version 1.7 is reported as
      supported when full scraping is done
    - When full scraping is not done, application/pdf version 1.7 is reported
      as not supported
    - Supported MIME type with made up version is reported as not supported
    - Made up MIME type with supported version is reported as not supported
"""
import os
from pathlib import Path

import pytest

from file_scraper.defaults import UNAV
from file_scraper.ghostscript.ghostscript_extractor import GhostscriptExtractor
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
            # 9.54.0: "Error: Tf refers to an unknown resource name"
            # 10.03.1: "startxref offset invalid"
            "stdout_part": "startxref offset invalid",
            "stderr_part": ""}),
        ("invalid_X_invalid_resource_name.pdf", {
            "purpose": "Test file has reference to unknown resource name.",
            "stdout_part": "error executing PDF token",
            "stderr_part": ""}),
        ("invalid_X_removed_xref.pdf", {
            "purpose": "Test xref change.",
            # 9.54.0: "Error:  An error occurred while reading an XREF"
            # 10.03.1: "xref entry not valid format"
            "stdout_part": "xref entry not valid format",
            "stderr_part": ""}),
    ]
)
def test_extractor_pdf(filename, result_dict, evaluate_extractor):
    """
    Test Ghostscript extractor.

    :filename: Test filename. Character X is replaced with versions 1.7,
               A-1a, A-2b, and A-3b. All of these files must be found.
    :result_dict: Result dict containing the test purpose, and parts of
                  expected results of stdout and stderr
    """
    for ver in ["1.7", "A-1a", "A-2b", "A-3b"]:
        filename = filename.replace("X", ver)
        correct = parse_results(filename, "application/pdf",
                                result_dict, True)
        extractor = GhostscriptExtractor(filename=correct.filename,
                                       mimetype="application/pdf")
        extractor.scrape_file()

        # Ghostscript cannot handle version or MIME type
        correct.streams[0]["version"] = UNAV
        correct.streams[0]["mimetype"] = UNAV

        evaluate_extractor(extractor, correct, eval_output=False)

        if extractor.well_formed:
            assert not partial_message_included("Error", extractor.messages())
            assert not extractor.errors()
        else:
            assert partial_message_included(correct.stderr_part,
                                            extractor.errors())
            assert partial_message_included(correct.stdout_part,
                                            extractor.errors())


def test_jpeg2000_inside_pdf(evaluate_extractor):
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

    extractor = GhostscriptExtractor(filename=correct.filename, mimetype=mimetype)
    extractor.scrape_file()

    # Ghostscript cannot handle version or MIME type
    correct.streams[0]["version"] = UNAV
    correct.streams[0]["mimetype"] = UNAV

    evaluate_extractor(extractor, correct, eval_output=False)


@pytest.mark.usefixtures("patch_shell_attributes_fx")
def test_ghostscript_returns_invalid_return_code():
    """Test that a correct error message is given
    when the tool gives an invalid return code"""
    mimetype = "application/pdf"
    path = os.path.join("tests/data", mimetype.replace("/", "_"))
    testfile = os.path.join(path, "valid_X.pdf")

    extractor = GhostscriptExtractor(filename=Path(testfile),
                                   mimetype=mimetype)

    extractor.scrape_file()

    assert "Ghostscript returned invalid return code: -1\n" in extractor.errors()


def test_is_supported():
    """Test is_supported method."""
    mime = "application/pdf"
    ver = "1.7"
    assert GhostscriptExtractor.is_supported(mime, ver, True)
    assert GhostscriptExtractor.is_supported(mime, None, True)
    assert not GhostscriptExtractor.is_supported(mime, ver, False)
    assert not GhostscriptExtractor.is_supported(mime, "foo", True)
    assert not GhostscriptExtractor.is_supported("foo", ver, True)


def test_tools():
    """Test verifies that tools will be returned"""
    extractor = GhostscriptExtractor(filename=Path("None"), mimetype="None")

    assert extractor.tools()["Ghostscript"]["version"] not in (UNAV, None)
