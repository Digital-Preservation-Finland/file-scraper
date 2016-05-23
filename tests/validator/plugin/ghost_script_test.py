"""
Test for pdf 1.7 ghostscript validator.
"""

import os
import sys
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from testcommon.settings import TESTDATADIR

from ipt.validator.ghost_script import GhostScript
from ipt.utils import UnknownException

BASEPATH = os.path.join(TESTDATADIR, '02_filevalidation_data', 'pdf_1_7')

FILEINFO = {
    "filename": "",
    "format": {
        "version": "1.7",
        "mimetype": "application/pdf"
    }
}


def test_pdf_1_7_ok():
    """
    test pdf 1.7
    """
    FILEINFO["filename"] = os.path.join(BASEPATH, "valid_1_7.pdf")
    validator = GhostScript(FILEINFO)
    (validity, messages, errors) = validator.validate()
    assert 'error' not in errors
    assert 'Error' not in messages
    assert validity is True


def test_pdf_1_7_validity_error():
    """
    test pdf 1.7
    """
    FILEINFO["filename"] = os.path.join(BASEPATH, "invalid_1_7.pdf")

    validator = GhostScript(FILEINFO)
    (validity, messages, errors) = validator.validate()

    assert 'Unrecoverable error, exit code 1' in errors
    assert 'Error: /undefined in obj' in messages
    assert validity is False


def test_pdf_1_7_version_error():
    """
    test pdf 1.7
    """
    FILEINFO["filename"] = os.path.join(BASEPATH, "invalid_wrong_version.pdf")

    validator = GhostScript(FILEINFO)
    (validity, messages, errors) = validator.validate()

    assert 'ERROR: wrong PDF version' in errors
    assert 'PDF document, version 1.3' in messages
    assert validity is False


def test_system_error(monkeypatch):
    """
    system error test
    """
    FILEINFO["filename"] = os.path.join(BASEPATH, "valid_1_7.pdf")
    validator = GhostScript(FILEINFO)
    monkeypatch.setattr(validator, 'cmd_exec', ['foo'])
    with pytest.raises(OSError):
        validator.validate()

    monkeypatch.setattr(validator, 'file_cmd_exec', ['foo'])
    with pytest.raises(OSError):
        validator.validate()

    FILEINFO["filename"] = os.path.join(BASEPATH, "foo.pdf")
    with pytest.raises(OSError):
        validator.validate()
