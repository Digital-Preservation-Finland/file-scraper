"""
Test for WarcTools.
"""
import os

import pytest

# Module to test
from ipt.validator.warctools import WarcTools
from ipt.validator.basevalidator import ValidatorError


@pytest.mark.usefixtures("monkeypatch_Popen")
@pytest.mark.parametrize(
    ["filename", "mimetype", "version"],
    [("warc_0_18/warc.0.18.warc", "application/warc", "0.18"),
     ("warc_0_17/valid.warc", "application/warc", "0.17"),
     ("warc_1_0/valid.warc.gz", "application/warc", "1.0"),
     ("arc/valid_arc.gz", "application/x-internet-archive", "1.0"),
     ("arc/valid_arc_no_compress", "application/x-internet-archive", "1.0"),
     ("warc_1_0/valid_no_compress.warc", "application/warc", "1.0")
    ])
def test_validate_valid(filename, mimetype, version):
    """Test cases for valid warcs and arcs."""

    validator = validate(
        os.path.join("tests/data/02_filevalidation_data", filename),
        mimetype,
        version)

    assert validator.is_valid, validator.errors() + validator.messages()
    assert 'OK' in validator.messages()
    assert validator.errors() == ""


@pytest.mark.usefixtures("monkeypatch_Popen")
@pytest.mark.parametrize(
    ["filename", "mimetype", "version", "errors"],
    [("warc_0_17/invalid.warc", "application/warc", "0.17",
      "zero length field name in format"),
     ("warc_0_17/valid.warc", "application/warc", "0.99",
      "File version check error"),
     ("warc_1_0/invalid.warc.gz", "application/warc", "1.0",
      "invalid distance code"),
     ("arc/invalid_arc.gz", "application/x-internet-archive",
      "1.0", "Not a gzipped file"),
     ("arc/invalid_arc_crc.gz", "application/x-internet-archive", "1.0",
      "CRC check failed")
    ])
def test_validate_invalid(filename, mimetype, version, errors):
    """Test cases for invalid warcs and arcs."""

    validator = validate(
        os.path.join("tests/data/02_filevalidation_data", filename),
        mimetype,
        version)

    assert not validator.is_valid, validator.errors()
    assert errors in validator.errors()


def test_system_error():
    """
    Test for system error(missing file)
    """

    with pytest.raises(ValidatorError) as error:
        validate("foo", "application/warc", "1.0")
    assert "No such file or directory" in str(error.value)


def validate(filename, mimetype, version):
    """
    Return validator with given filename
    """

    fileinfo = {
        "filename": filename,
        "format": {
            "mimetype": mimetype,
            "version": version
        }
    }

    validator = WarcTools(fileinfo)
    validator.validate()
    return validator
