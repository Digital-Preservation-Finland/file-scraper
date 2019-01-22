"""Test the ipt.validator.pngcheck module"""

import os

import ipt.validator.pngcheck


def validate(filename):
    """Return validator with given filename"""

    metadata_info = {
        "filename": os.path.join(
            'tests/data/02_filevalidation_data/png', filename),
        "format": {
            "mimetype": 'image/png',
            "version": '1.21.21.2'}}

    val = ipt.validator.pngcheck.Pngcheck(metadata_info)
    val.validate()
    return val


def test_pngcheck_valid():
    """Test valid PNG file"""

    val = validate('valid.png')

    assert val.is_valid
    assert 'OK' in val.messages()
    assert val.errors() == ""


def test_pngcheck_invalid():
    """Test corrupted PNG file"""

    val = validate('invalid.png')

    assert not val.is_valid
    assert 'OK' not in val.messages()
    assert 'ERROR' in val.errors()
