"""
Test for WarcTools.
"""
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

import pytest
import testcommon.settings

# Module to test
from ipt.validator.warctools import WarcTools
from ipt.utils import UnknownException
from ipt.validator.basevalidator import ValidatorError

PROJECTDIR = testcommon.settings.PROJECTDIR

TESTDATADIR_BASE = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                '../../data'))

TESTDATADIR = os.path.abspath(os.path.join(TESTDATADIR_BASE,
                                           '02_filevalidation_data'))


@pytest.mark.usefixtures("monkeypatch_Popen")
@pytest.mark.parametrize(
    ["filename", "mimetype", "version", "validity", "messages"],
    [("warc_0_18/warc.0.18.warc", "application/warc", "0.18", True, ""),
     ("warc_0_17/valid.warc", "application/warc", "0.17", True, ""),
     ("warc_1_0/valid.warc.gz", "application/warc", "1.0", True, ""),
     ("arc/valid_arc.gz", "application/x-internet-archive",
        "1.0", True, ""),
     ("arc/valid_arc_no_compress", "application/x-internet-archive",
        "1.0", True, ""),
     ("warc_1_0/valid_no_compress.warc", "application/warc", "1.0", True, "")
     ])
def test_validate_valid(filename, mimetype, version, validity, messages):
    """Test cases for valid warcs and arcs."""

    fileinfo = {
        "filename": os.path.join(TESTDATADIR, filename),
        "format": {
            "mimetype": mimetype,
            "version": version
        }
    }

    validator = WarcTools(fileinfo)
    validator.validate()
    assert validator.is_valid, validator.errors() + validator.messages()
    assert 'OK' in validator.messages()
    assert validator.errors() == ""


@pytest.mark.usefixtures("monkeypatch_Popen")
@pytest.mark.parametrize(
    ["filename", "mimetype", "version", "validity", "errors"],
    [("warc_0_17/invalid.warc", "application/warc", "0.17", False,
        "zero length field name in format"),
    ("warc_0_17/valid.warc", "application/warc", "0.99", False,
        "File version check error"),
    ("warc_1_0/invalid.warc.gz", "application/warc", "1.0", False,
        "invalid distance code"),
    ("arc/invalid_arc.gz", "application/x-internet-archive",
        "1.0", False, "Not a gzipped file"),
     ("arc/invalid_arc_crc.gz", "application/x-internet-archive", "1.0",
        False, "CRC check failed")
     ])
def test_validate_invalid(filename, mimetype, version, validity, errors):
    """Test cases for invalid warcs and arcs."""

    fileinfo = {
        "filename": os.path.join(TESTDATADIR, filename),
        "format": {
            "mimetype": mimetype,
            "version": version
        }
    }

    validator = WarcTools(fileinfo)
    validator.validate()
    assert not validator.is_valid, validator.errors()
    assert 'OK' not in validator.messages()
    assert errors in validator.errors()
    


def test_system_error():
    """
    Test for system error(missing file)
    """
    fileinfo = {
        "filename": "foo",
        "format": {
            "mimetype": "application/warc",
            "version": "1.0"
        }
    }
    validator = WarcTools(fileinfo)
    with pytest.raises(ValidatorError) as error:
        validator.validate()
        assert "No such file or directory" in str(error.value)

