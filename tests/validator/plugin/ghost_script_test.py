"""
Test for pdf 1.7 ghostscript validator.
"""

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from testcommon.settings import TESTDATADIR

from ipt.validator.ghost_script import GhostScript

BASEPATH = os.path.join(TESTDATADIR, '02_filevalidation_data', 'pdf_1_7')


def test_pdf_1_7():
    """
    test pdf 1.7
    """

    # OK
    fileinfo = {
        "filename": os.path.join(BASEPATH, "valid_1_7.pdf"),
        "format": {
            "version": "1.7",
            "mimetype": "application/pdf"
        }
    }
    validator = GhostScript(fileinfo)
    (validity, messages, errors) = validator.validate()
    assert 'error' not in errors
    assert 'Error' not in messages
    assert validity is True

    # Validity error
    fileinfo = {
        "filename": os.path.join(BASEPATH, "invalid_1_7.pdf"),
        "format": {
            "version": "1.7",
            "mimetype": "application/pdf"
        }
    }
    validator = GhostScript(fileinfo)
    (validity, messages, errors) = validator.validate()

    assert 'Unrecoverable error, exit code 1' in errors
    assert 'Error: /undefined in obj' in messages
    assert validity is False

    # Version error
    fileinfo = {
        "filename": os.path.join(BASEPATH, "invalid_wrong_version.pdf"),
        "format": {
            "version": "1.7",
            "mimetype": "application/pdf"
        }
    }
    validator = GhostScript(fileinfo)
    (validity, messages, errors) = validator.validate()

    assert 'ERROR: wrong PDF version' in errors
    assert 'PDF document, version 1.3' in messages
    assert validity is False
