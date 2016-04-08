# encoding=utf8
# Common boilerplate
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(
                os.path.dirname(__file__), '..')))
reload(sys)
sys.setdefaultencoding("utf-8")
import testcommon.settings
import json

# Module to test
import ipt.validator.filelist
import ipt.mets.parser

import ipt.validator.plugin.mockup

# Other imports
import random
import string
import testcommon.shell

PROJECTDIR = testcommon.settings.PROJECTDIR

TESTDATADIR_BASE = os.path.abspath(os.path.join(
    os.path.dirname(__file__),
    '../data'))

TESTDATADIR = os.path.abspath(os.path.join(
    TESTDATADIR_BASE,
    '02_filevalidation_data'))

SHARE_PATH = os.path.abspath(os.path.os.path.join(
    os.path.dirname(__file__),
    '../../',
    'include/share'))

TEST_CONFIG_FILENAME = os.path.join(SHARE_PATH, 'validators/validators.json')


class TestMetsFileValidator:
    pass
