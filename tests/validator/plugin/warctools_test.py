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
    ["filename", "mimetype", "version", "exitcode", "stdout", "stderr"],
    [("warc_0_18/warc.0.18.warc", "application/warc", "0.18", True, "", ""),
     ("warc_0_17/valid.warc", "application/warc", "0.17", True, "", ""),
     ("warc_0_17/valid.warc", "application/warc", "0.99", False, "", ""),
     ("warc_0_17/invalid.warc", "application/warc", "0.17", False, "",
        "zero length field name in format"),
     ("warc_1_0/valid.warc.gz", "application/warc", "1.0", True, "", ""),
     ("warc_1_0/invalid.warc.gz", "application/warc", "1.0", False, "",
        "invalid distance code"),
     ("arc/valid_arc.gz", "application/x-internet-archive",
        "1.0", True, "", "DrinkingWithBob-MadonnaAdoptsAfricanBaby"),
     ("arc/valid_arc_no_compress", "application/x-internet-archive",
        "1.0", True, "", "DrinkingWithBob-MadonnaAdoptsAfricanBaby"),
     ("arc/invalid_arc.gz", "application/x-internet-archive",
        "1.0", False, "", "Not a gzipped file"),
     ("warc_1_0/valid_no_compress.warc", "application/warc", "1.0", True,
        "", ""),
     ("arc/invalid_arc_crc.gz", "application/x-internet-archive", "1.0",
        False, "", "CRC check failed")])
def test_validate(filename, mimetype, version, exitcode, stdout, stderr):
    """Test cases for valid/invalid warcs and arcs."""

    fileinfo = {
        "filename": os.path.join(TESTDATADIR, filename),
        "format": {
            "mimetype": mimetype,
            "version": version
        }
    }

    validator = WarcTools(fileinfo)
    (exitcode_result, stderr_result, stdout_result) = validator.validate()
    assert exitcode == exitcode_result
    assert stdout in stdout_result
    assert stderr in stderr_result
    print stdout, stderr


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
