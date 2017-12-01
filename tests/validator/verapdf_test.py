"""
Tests for VeraPDF validator.
"""

import os
import pytest
import lxml.etree as ET
from ipt.validator.verapdf import VeraPDF


BASEPATH = "tests/data/02_filevalidation_data/"


@pytest.mark.parametrize(
    ['filename', 'is_valid', 'errors', 'version'],
    [
        ["pdfa-1/valid.pdf", True, "", 'A-1b'],
        ["pdfa-2/pdfa2-pass-a.pdf", True, "", 'A-2b'],
        ["pdfa-3/pdfa3-pass-a.pdf", True, "", 'A-3b'],
        ["pdfa-1/valid.pdf", False,
         "not compliant with Validation Profile requirements", 'A-1a'],
        ["pdfa-1/invalid.pdf", False,
         "doesn't appear to be a valid PDF", 'A-1b'],
        ["pdfa-2/pdfa2-fail-a.pdf", False,
         "not compliant with Validation Profile requirements", 'A-2b'],
        ["pdfa-3/pdfa3-fail-a.pdf", False,
         "not compliant with Validation Profile requirements", 'A-3b'],
    ]
)
def test_validate_valid_file(filename, is_valid, errors, version):
    """
    Test validation of PDF/A files.
    """

    fileinfo = {
        'filename': os.path.join(BASEPATH, filename),
        'format': {
            'mimetype': "application/pdf",
            'version': version
        }
    }

    validator = VeraPDF(fileinfo)
    validator.validate()

    # Is validity expected?
    assert validator.is_valid == is_valid

    # Is stderr output expected?
    if errors == "":
        assert validator.errors() == ""
    else:
        assert errors in validator.errors()
