"""
Test for pdf 1.7 ghostscript validator.
"""

import os

from ipt.validator.ghostscript import GhostScript

BASEPATH = "tests/data/02_filevalidation_data/pdf_1_7"

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
    FILEINFO["filename"] = os.path.join(BASEPATH, "valid_1_7.pdf")
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
    FILEINFO["filename"] = os.path.join(BASEPATH, "invalid_1_7.pdf")

    validator = GhostScript(FILEINFO)
    validator.validate()

    assert 'Unrecoverable error, exit code 1' in validator.errors()
    assert 'Error: /undefined in obj' in validator.messages()
    assert not validator.is_valid


def test_pdf_1_7_version_error():
    """
    test pdf 1.7 wrong version case
    """
    FILEINFO["filename"] = os.path.join(BASEPATH, "invalid_wrong_version.pdf")

    validator = GhostScript(FILEINFO)
    validator.validate()

    assert 'ERROR: wrong file version. Expected PDF 1.7,' \
        ' found PDF document, version 1.3' in validator.errors()
    assert 'PDF document, version 1.3' in validator.messages()
    assert not validator.is_valid
