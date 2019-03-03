"""
Tests for PSPP validator.
"""

import os
import pytest
from ipt.validator.pspp import PSPP


BASEPATH = "tests/data/02_filevalidation_data/pspp"


@pytest.mark.parametrize(
    ['filename', 'mimetype', 'version', 'validity'],
    [
        ("ISSP2000_sample.por", "application/x-spss-por", "", True),
        ("empty.por", "application/x-spss-por", "", False),
        ("example.sps", "application/x-spss-por", "", False),
        ("ISSP2000_sample.sav", "application/x-spss-por", "", False),
        ("ISSP2000_sample_corrupted.por", "application/x-spss-por", "", False),
    ]
)
def test_validate_valid_file(filename, mimetype, version, validity):

    metadata_info = {
        'filename': os.path.join(BASEPATH, filename),
        'format': {
            'mimetype': mimetype,
            'version': version
        }
    }

    validator = PSPP(metadata_info)
    validator.validate()
    assert validator.is_valid == validity
