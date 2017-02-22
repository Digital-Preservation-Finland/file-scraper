"""
Tests for ImageMagick validator.
"""

import os
import pytest
from ipt.validator.imagemagick import ImageMagick


BASEPATH = "tests/data/02_filevalidation_data/imagemagick"


@pytest.mark.parametrize(
    ['filename', 'mimetype', 'version'],
    [
        ("valid_dpx.dpx", "image/dpx", "2.0"),
        ("valid_png.png", "image/png", "2.0"),
    ]
)


def test_validate_valid_file(filename, mimetype, version):

    fileinfo = {
        'filename': os.path.join(BASEPATH, filename),
        'format': {
            'mimetype': mimetype,
            'version': version
        }
    }

    validator = ImageMagick(fileinfo)
    validator.validate()
    assert validator.is_valid


@pytest.mark.parametrize(
    ['filename', 'mimetype', 'version'],
    [
        ("corrupted_dpx.dpx", "image/dpx", "2.0"),
        ("valid_png.png", "image/dpx", "2.0"),
        ("empty_file.dpx", "image/dpx", "2.0"),
    ]
)


def test_validate_invalid_file(filename, mimetype, version):

    fileinfo = {
        'filename': os.path.join(BASEPATH, filename),
        'format': {
            'mimetype': mimetype,
            'version': version
        }
    }

    validator = ImageMagick(fileinfo)
    validator.validate()
    assert not validator.is_valid
