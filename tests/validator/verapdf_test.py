"""
Tests for VeraPDF validator for PDF/A files.
"""

import os
import pytest
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
         "Couldn't parse stream caused by exception", 'A-1b'],
        ["pdfa-2/pdfa2-fail-a.pdf", False,
         "not compliant with Validation Profile requirements", 'A-2b'],
        ["pdfa-3/pdfa3-fail-a.pdf", False,
         "not compliant with Validation Profile requirements", 'A-3b'],
        ["tiff/valid.tif", False,
         "SEVERE", 'A-3b'],
    ]
)
def test_validate_file(filename, is_valid, errors, version):
    """
    Test validation of PDF/A files. Asserts that valid files are
    validated and invalid files or files with wrong versions are
    not validated. Also asserts that files which aren't PDF files
    are processed correctly.
    """

    metadata_info = {
        'filename': os.path.join(BASEPATH, filename),
        'format': {
            'mimetype': "application/pdf",
            'version': version
        }
    }

    validator = VeraPDF(metadata_info)
    validator.validate()

    # Is validity expected?
    assert validator.is_valid == is_valid

    # Is stderr output expected?
    if errors == "":
        assert validator.errors() == ""
    else:
        assert errors in validator.errors()
