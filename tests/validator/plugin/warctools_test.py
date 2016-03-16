"""
Test for WarcTools.
"""
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

import pytest
import testcommon.settings

# Module to test
from ipt.validator.plugin.warctools import WarcTools, WarcError
from ipt.utils import UnknownException

PROJECTDIR = testcommon.settings.PROJECTDIR

TESTDATADIR_BASE = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                '../../data'))

TESTDATADIR = os.path.abspath(os.path.join(TESTDATADIR_BASE,
                                           '02_filevalidation_data'))


@pytest.mark.usefixtures("monkeypatch_Popen")
@pytest.mark.parametrize(
    ["filename", "mimetype", "version", "exitcode", "stdout", "stderr"],
    [("warc_0_17/valid.warc", "application/warc", "0.17", 0, "", ""),
     ("warc_0_17/valid.warc", "application/warc", "0.99", 117, "", ""),
     ("warc_0_17/invalid.warc", "application/warc", "0.17", 117, "",
        "zero length field name in format"),
     ("warc_1_0/valid.warc.gz", "application/warc", "1.0", 0, "", ""),
     ("warc_1_0/invalid.warc.gz", "application/warc", "1.0", 117, "",
        "invalid distance code"),
     ("arc/valid_arc.gz", "application/x-internet-archive",
        "1.0", 0, "", "DrinkingWithBob-MadonnaAdoptsAfricanBaby"),
     ("arc/valid_arc_no_compress", "application/x-internet-archive",
        "1.0", 0, "", "DrinkingWithBob-MadonnaAdoptsAfricanBaby"),
     ("arc/invalid_arc.gz", "application/x-internet-archive",
        "1.0", 117, "", "Not a gzipped file"),
     ("warc_1_0/valid_no_compress.warc", "application/warc", "1.0", 0,
        "", "")])
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
    (exitcode_result, stdout_result, stderr_result) = validator.validate()
    assert exitcode == exitcode_result
    assert stdout in stdout_result
    assert stderr in stderr_result
    print stdout, stderr


def test_system_error():
    """
    Test for system error(missing file)
    """
    with pytest.raises(UnknownException):

        fileinfo = {
            "filename": "foo",
            "format": {
                "mimetype": "application/warc",
                "version": "1.0"
            }
        }
        validator = WarcTools(fileinfo)
        validator.validate()

    with pytest.raises(WarcError):
        fileinfo = {
            "filename": "foo",
            "format": {
                "mimetype": "foo",
                "version": "1.0"
            }
        }

        validator = WarcTools(fileinfo)
