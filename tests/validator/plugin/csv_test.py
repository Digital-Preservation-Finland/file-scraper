"""
Test for WarcTools.
"""
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

import pytest
import testcommon.settings

# Module to test
from ipt.validator.plugin.csv_validator import Csv

PROJECTDIR = testcommon.settings.PROJECTDIR

TESTDATADIR_BASE = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                '../../data'))

TESTDATADIR = os.path.abspath(os.path.join(TESTDATADIR_BASE,
                                           '02_filevalidation_data'))
JPEG_PATH = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        '../../data/06_mets_validation/sips/fd2009-00002919-preservation/access_img/img0008-access.jpg'))


def test_validate_success():
    """Test case for valid csv"""
    file_path = os.path.join(TESTDATADIR, "mock_data.csv")
    validator = Csv("text/csv", "UTF-8", file_path)
    (exitcode_result, stdout_result, stderr_result) = validator.validate()
    assert exitcode_result == 0
    assert len(stdout_result) == 0
    assert len(stderr_result) == 0


def test_validate_fail():
    """Test case for invalid csv"""
    # It's hard to get the csv module to fail, feed it a JPG file and it will
    validator = Csv("text/csv", "UTF-8", JPEG_PATH)
    (exitcode_result, stdout_result, stderr_result) = validator.validate()
    assert exitcode_result == 1
    assert len(stdout_result) == 0
    assert len(stderr_result) != 0
    print stderr_result
