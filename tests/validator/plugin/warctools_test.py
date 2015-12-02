# Common boilerplate
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

import re
import json
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


def test_validate_warc():

    testcasefile = os.path.join(PROJECTDIR, TESTDATADIR,
                                'warctools_testcases.json')
    print "\nLoading test configuration from %s\n" % testcasefile

    json_data = open(testcasefile)
    testcases = json.load(json_data)
    json_data.close()

    for testcase in testcases["test_validate"]:

        print "%s: %s" % (testcase["testcase"], testcase["filename"])

        testcase["filename"] = os.path.join(
            testcommon.settings.TESTDATADIR, testcase["filename"])
        val = ipt.validator.plugin.warctools.WarcTools(
            testcase["mimetype"],
            testcase["formatVersion"],
            testcase["filename"])

        (status, stdout, stderr) = val.validate()


        assert testcase["expected_result"]["status"] == status


        for match_string in testcase["expected_result"]["stdout"]:
            message = "\n".join(
                ["got:", stdout.decode('utf-8'), "expected:",
                 match_string])
            assert re.match('(?s).*' + match_string, stdout), message

        for match_string in testcase["expected_result"]["stderr"]:
            message = "\n".join(
                ["got:", stderr.decode('utf-8'), "expected:",
                 match_string])
            assert re.match('(?s).*' + match_string, stderr), message
