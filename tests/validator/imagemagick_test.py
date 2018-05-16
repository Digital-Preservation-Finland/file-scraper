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
        ("valid_jpeg.jpeg", "image/jpeg", "1.01"),
        ("valid_jp2.jp2", "image/jp2", ""),
        ("valid_tiff.tiff", "image/tiff", "6.0"),
    ]
)


def test_validate_valid_file(filename, mimetype, version):

    metadata_info = {
        'filename': os.path.join(BASEPATH, filename),
        'format': {
            'mimetype': mimetype,
            'version': version
        }
    }

    validator = ImageMagick(metadata_info)
    validator.validate()
    assert validator.is_valid


@pytest.mark.parametrize(
    ['filename', 'mimetype', 'version'],
    [
        ("valid_png.png", "image/x-dpx", "")
    ]
)


def test_validate_invalid_file(filename, mimetype, version):

    metadata_info = {
        'filename': os.path.join(BASEPATH, filename),
        'format': {
            'mimetype': mimetype,
            'version': version
        }
    }

    validator = ImageMagick(metadata_info)
    validator.validate()
    assert not validator.is_valid
