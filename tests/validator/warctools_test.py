"""Test the ipt.validator.warctools module"""
import os

import pytest

# Module to test
from ipt.validator.warctools import WarctoolsWARC, WarctoolsARC


@pytest.mark.parametrize(
    ['filename', 'version'],
    [('warc_0_18/warc.0.18.warc', '0.18'),
     ('warc_0_17/valid.warc', '0.17'),
     ('warc_1_0/valid.warc.gz', '1.0'),
     ('warc_1_0/valid_no_compress.warc', '1.0')])
def test_validate_valid_warc(filename, version):

    metadata_info = {
        'filename': os.path.join("tests/data/02_filevalidation_data", filename),
        'format': {
            'mimetype': 'application/warc',
            'version': version
        }
    }

    validator = WarctoolsWARC(metadata_info)
    validator.validate()

    assert validator.is_valid


@pytest.mark.parametrize(
    ['filename', 'version', 'error'],
    [('warc_0_17/invalid.warc', '0.17', 'incorrect newline in header'),
     ('warc_0_17/valid.warc', '666.66', 'version check error'),
     ('warc_1_0/invalid.warc.gz', '1.0', 'invalid distance code'),
     ('warc_0_18/invalid_warc.0.18.warc', '0.18', 'invalid header')])
@pytest.mark.timeout(5)
def test_validate_invalid_warc(filename, version, error):

    metadata_info = {
        'filename': os.path.join("tests/data/02_filevalidation_data", filename),
        'format': {
            'mimetype': 'application/warc',
            'version': version
        }
    }

    validator = WarctoolsWARC(metadata_info)
    validator.validate()

    assert not validator.is_valid
    assert error in validator.errors()


@pytest.mark.parametrize(
    ['filename', 'version'],
    [('arc/valid_arc.gz', '1.0'),
     ('arc/valid_arc_no_compress', '1.0')])
def test_validate_valid_arc(filename, version):

    metadata_info = {
        'filename': os.path.join("tests/data/02_filevalidation_data", filename),
        'format': {
            'mimetype': 'application/x-internet-archive',
            'version': version
        }
    }

    validator = WarctoolsARC(metadata_info)
    validator.validate()

    assert validator.is_valid


@pytest.mark.parametrize(
    ['filename', 'version', 'error'],
    [('arc/invalid_arc.gz', '1.0', 'Not a gzipped file'),
     ('arc/invalid_arc_crc.gz', '1.0', 'CRC check failed')])
def test_validate_invalid_arc(filename, version, error):

    metadata_info = {
        'filename': os.path.join("tests/data/02_filevalidation_data", filename),
        'format': {
            'mimetype': 'application/x-internet-archive',
            'version': version
        }
    }

    validator = WarctoolsARC(metadata_info)
    validator.validate()

    assert not validator.is_valid
    assert error in validator.errors()
