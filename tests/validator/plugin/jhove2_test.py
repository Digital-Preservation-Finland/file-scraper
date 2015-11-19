# Common boilerplate
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

import re
import json
import pytest
import testcommon.settings

# Module to test
from ipt.validator.plugin import jhove2

PROJECTDIR = testcommon.settings.PROJECTDIR

TESTDATADIR_BASE = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                '../../data'))

TESTDATADIR = os.path.abspath(os.path.join(TESTDATADIR_BASE,
                                           '02_filevalidation_data',
                                           'warc_1_0'))

@pytest.mark.parametrize('case', [
#    'converted-KK-20131120090606-00002-ark8.lib.helsinki.fi.warc',
#    'KK-20131120090606-00002-ark8.lib.helsinki.fi.arc.gz',
#    'IAH-20131121091702-00000-ark8.lib.helsinki.fi.warc.gz',
    'valid.warc.gz'
    ])
def test_valid_warcs(case):
    """Test cases for valid warcs."""
    path = os.path.join(TESTDATADIR, case)
    print path
    os.path.isfile(path)
    validator = jhove2.Jhove2(
        mimetype='application/warc',
        fileversion='1.0',
        filename=path)
    result = validator.validate()
    #print result
    #assert 1 == 0
