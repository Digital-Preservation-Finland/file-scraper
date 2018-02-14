"""
Tests for Vnu validator.
"""

import os
import pytest
from ipt.validator.vnu import Vnu


BASEPATH = "tests/data/02_filevalidation_data/html/"


@pytest.mark.parametrize(
    [
        'filename',
        'is_valid',
        'errors'
    ],
    [
        [
            "valid_html5.html",
            True,
            ""
        ],
        [
            "invalid_html5_wrong_encoding.html",
            False,
            "Internal encoding declaration"
        ],
    ]
)
def test_validate_valid_file(filename, is_valid, errors):
    """
    Test validation of HTML5 files.
    """

    metadata_info = {
        'filename': os.path.join(BASEPATH, filename),
        'format': {
            'mimetype': "text/html",
            'version': "5.0"
        }
    }

    validator = Vnu(metadata_info)
    validator.validate()

    # Is validity expected?
    assert validator.is_valid is is_valid

    # Is stderr output expected?
    if errors == "":
        assert validator.errors() == ""
    else:
        assert errors in validator.errors()

    # Is stdout output expected?
    assert metadata_info['filename'] + "\n" == validator.messages()

