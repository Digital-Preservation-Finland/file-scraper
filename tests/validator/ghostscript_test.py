"""
Test for pdf 1.7 ghostscript validator.
"""

import os

from ipt.validator.ghostscript import GhostScript

BASEPATH = "tests/data/02_filevalidation_data"

FILEINFO = {
    "filename": "",
    "format": {
        "version": "1.7",
        "mimetype": "application/pdf"
    }
}


def test_pdf_1_7_ok():
    """
    test pdf 1.7 ok case
    """
    FILEINFO["filename"] = os.path.join(BASEPATH, "pdf_1_7", "valid_1_7.pdf")
    validator = GhostScript(FILEINFO)
    validator.validate()
    assert 'Error' not in validator.messages()
    assert validator.messages() != ""
    assert validator.is_valid
    assert validator.errors() == ""


def test_pdf_1_7_validity_error():
    """
    test pdf 1.7 invalid case
    """
    FILEINFO["filename"] = os.path.join(BASEPATH, "pdf_1_7", "invalid_1_7.pdf")

    validator = GhostScript(FILEINFO)
    validator.validate()

    assert 'Unrecoverable error, exit code 1' in validator.errors()
    assert 'Error: /undefined in obj' in validator.messages()
    assert not validator.is_valid


def test_pdf_1_7_version_error():
    """
    test pdf 1.7 wrong version case
    """
    FILEINFO["filename"] = os.path.join(BASEPATH, "pdf_1_7",
                                        "invalid_wrong_version.pdf")

    validator = GhostScript(FILEINFO)
    validator.validate()

    assert 'ERROR: wrong file version. Expected PDF 1.7,' \
        ' found PDF document, version 1.3' in validator.errors()
    assert 'PDF document, version 1.3' in validator.messages()
    assert not validator.is_valid


def test_pdfa_valid():
    """Test that valid PDF/A is valid
       This file is also used in veraPDF test, where it should result "valid".
    """
    FILEINFO["filename"] = os.path.join(BASEPATH, "pdfa-1", "valid.pdf")
    FILEINFO["format"]["version"] = "A-1b"
    validator = GhostScript(FILEINFO)
    validator.validate()
    assert 'Error' not in validator.messages()
    assert validator.messages() != ""
    assert validator.is_valid
    assert validator.errors() == ""


def test_pdf_valid_pdfa_invalid():
    """Test that valid PDF (but invalid PDF/A) is valid.
       This file is also used in veraPDF test, where it should result
       "invalid".
    """
    FILEINFO["filename"] = os.path.join(BASEPATH, "pdfa-3", "pdfa3-fail-a.pdf")
    FILEINFO["format"]["version"] = "A-3a"
    validator = GhostScript(FILEINFO)
    validator.validate()
    assert 'Error' not in validator.messages()
    assert validator.messages() != ""
    assert validator.is_valid
    assert validator.errors() == ""


def test_pdf_invalid_pdfa_invalid():
    """Test that valid PDF (but invalid PDF/A) is valid.
       This file is also used in veraPDF test, where it should result
       "invalid".
    """
    FILEINFO["filename"] = os.path.join(BASEPATH, "pdfa-1", "invalid.pdf")
    FILEINFO["format"]["version"] = "A-1b"
    validator = GhostScript(FILEINFO)
    validator.validate()
    assert not validator.is_valid
    assert "An error occurred while reading an XREF table." in \
        validator.errors()
