"""
Test for WarcTools.
"""
import os
import sys
import io
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


def test_validate_success_wikipedia(testpath):
    """Test the validator with valid data from Wikipedia's CSV article"""
    csv_path = os.path.join(testpath, 'csv.csv')
    techmd = {
        "mimetype": "text/csv",
        "filename": csv_path,
        "separator": "CR+LF",
        "delimiter": ";",
        "charset": "UTF-8",
        "header_fields": ""}
    with io.open(csv_path, 'w', newline='\r\n') as target:
        target.write(u'1997,Ford,E350,"ac, abs, moon",3000.00\n')
        target.write(u'1999,Chevy,"Venture ""Extended Edition""","",4900.00\n')
        target.write(u'1999,Chevy,"Venture ""Extended Edition, Very Large""",,'
                     '5000.00\n')
        target.write(u'''1996,Jeep,Grand Cherokee,"MUST SELL!
air, moon roof, loaded",4799.00''' + u'\n')

    validator = Csv(techmd)
    (exitcode_result, stdout_result, stderr_result) = validator.validate()
    assert exitcode_result == 0
    assert len(stdout_result) == 0
    assert len(stderr_result) == 0


def test_validate_fail_jpeg():
    """Test case for invalid csv"""
    # It's hard to get the csv module to fail, feed it a JPG file and it will
    techmd = {
        "mimetype": "text/csv",
        "filename": JPEG_PATH,
        "separator": "CR+LF",
        "delimiter": ";",
        "charset": "UTF-8",
        "header_fields": ""}
    validator = Csv(techmd)
    (exitcode_result, stdout_result, stderr_result) = validator.validate()
    assert exitcode_result == 1
    assert len(stdout_result) == 0
    assert len(stderr_result) != 0
    print stderr_result


def test_validate_fail_wikipedia(testpath):
    """Test the validator with invalid data based on Wikipedia's CSV article"""
    csv_path = os.path.join(testpath, 'csv.csv')
    techmd = {
        "mimetype": "text/csv",
        "filename": csv_path,
        "separator": "CR+LF",
        "delimiter": ";",
        "charset": "UTF-8",
        "header_fields": ""}
    with io.open(csv_path, 'w', newline='\r\n') as target:
        target.write(u'1999,Chevy,"Venture ""Extended Edition"","",4900.00\n')

    validator = Csv(techmd)
    (exitcode_result, stdout_result, stderr_result) = validator.validate()
    assert exitcode_result == 1
    assert len(stdout_result) == 0
    assert len(stderr_result) != 0
    print stderr_result
