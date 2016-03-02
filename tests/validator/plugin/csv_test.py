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


def test_validate():
    """Test cases for valid/invalid warcs and arcs."""
    file_path = os.path.join(TESTDATADIR, "mock_data.csv")
    validator = Csv("text/csv", "UTF-8", file_path)
    (exitcode_result, stdout_result, stderr_result) = validator.validate()
    assert exitcode_result == 0
    assert len(stdout_result) == 0
    assert len(stderr_result) == 0
