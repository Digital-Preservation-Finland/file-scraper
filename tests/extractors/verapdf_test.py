"""
Tests for VeraPDF extractor for PDF/A files.

This module tests that:
    - For pdf versions A-1a, A-2b and A-3b, MIME type, version, streams and
      well-formedness are scraped correctly. This is tested using one
      well-formed file and two erroneous ones (one with altered payload and
      one in which a xref entry has been removed) for each version.
    - For well-formed files, extractor messages contain "PDF file is compliant
      with Validation Profile requirements".
    - For the files with altered payload, extractor errors contain "can not
      locate xref table".
    - For the files with removed xref entry, extractor errors contain "In a
      cross reference subsection header".
    - For files that are valid PDF 1.7 or 1.4 but not valid PDF/A, MIME type,
      version and streams are scraped correctly but they are reported as
      not well-formed.
    - Extractor can be run for files without PDF extension.
    - The extractor supports MIME type application/pdf with versions A-1b
      when well-formedness is checked, but does not support them when
      well-formedness is not checked. The extractor also does not support made
      up MIME types or versions.
"""
from pathlib import Path

import pytest

from file_scraper.verapdf.verapdf_extractor import VerapdfExtractor
from tests.common import (parse_results, partial_message_included)

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
            "stderr_part": "End of file is reached"}),
    ]
)
def test_extractor(filename, result_dict, evaluate_extractor):
    """
    Test extractor with PDF/A.

    :filename: Test file name
    :result_dict: Result dict containing test purpose, and parts of
                  expected results of stdout and stderr
    """
    for ver in ["A-1a", "A-2b", "A-3b"]:
        filename = filename.replace("X", ver)
        correct = parse_results(filename, MIMETYPE,
                                result_dict, True)
        extractor = VerapdfExtractor(filename=correct.filename,
                                   mimetype=MIMETYPE)
        extractor.extract()

        if not correct.well_formed:
            assert not extractor.well_formed
            assert partial_message_included(correct.stdout_part,
                                            extractor.messages())
            assert partial_message_included(correct.stderr_part,
                                            extractor.errors())
        else:
            evaluate_extractor(extractor, correct)


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
def test_extractor_invalid_pdfa(filename, result_dict, evaluate_extractor):
    """
    Test extractor with files that are not valid PDF/A.

    :filename: Test file name
    :result_dict: Result dict containing test purpose, and parts of
                  expected results of stdout and stderr
    """
    correct = parse_results(filename, MIMETYPE,
                            result_dict, True)
    extractor = VerapdfExtractor(filename=correct.filename,
                               mimetype=MIMETYPE)
    extractor.extract()

    if not correct.well_formed:
        assert not extractor.well_formed
        assert partial_message_included(correct.stdout_part,
                                        extractor.messages())
        assert partial_message_included(correct.stderr_part,
                                        extractor.errors())
    else:
        evaluate_extractor(extractor, correct)


def test_extractor_no_file_extension(evaluate_extractor):
    """Test extractor with a PDF file that doesn't have a file extension."""
    filename = "valid_A-3b_no_file_extension"
    result_dict = {
        "purpose": "Test valid file without file extension.",
        "stdout_part": "PDF file is compliant with Validation Profile "
                       "requirements.",
        "stderr_part": ""
    }
    correct = parse_results(filename, MIMETYPE, result_dict, True)
    extractor = VerapdfExtractor(filename=correct.filename, mimetype=MIMETYPE)
    extractor.extract()

    evaluate_extractor(extractor, correct)


@pytest.mark.usefixtures("patch_shell_attributes_fx")
def test_verapdf_returns_invalid_return_code():
    """Test that a correct error message is given
    when the tool gives an invalid return code"""
    path = Path("tests/data", MIMETYPE.replace("/", "_"))
    testfile = path / "valid_X.pdf"

    extractor = VerapdfExtractor(filename=testfile,
                               mimetype=MIMETYPE)

    extractor.extract()

    assert "VeraPDF returned invalid return code: -1" in extractor.errors()


def test_is_supported():
    """Test is_supported method."""
    mime = MIMETYPE
    ver = "A-1b"
    assert VerapdfExtractor.is_supported(mime, ver, True)
    assert VerapdfExtractor.is_supported(mime, None, True)
    assert not VerapdfExtractor.is_supported(mime, ver, False)
    assert not VerapdfExtractor.is_supported(mime, "foo", True)
    assert not VerapdfExtractor.is_supported("foo", ver, True)


def test_tools():
    """
    Test that correct software is received and
    that the version number starts with a digit
    """
    tool_extractor = VerapdfExtractor(filename=Path(""), mimetype="")
    assert tool_extractor.tools()["veraPDF"]["version"][0].isdigit()
