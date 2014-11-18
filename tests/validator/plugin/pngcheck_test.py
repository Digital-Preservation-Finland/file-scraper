# Common boilerplate
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

import re
import pytest
import testcommon.settings
from testcommon.casegenerator import pytest_generate_tests

# Module to test
import ipt.validator.plugin.pngcheck

# VALIDATORS_CONFIG_FILENAME = os.path.join(testcommon.settings.SHAREDIR,
#                                          'validators/validators.json')


class TestJhoveFilevalidator:

    testcases = {
        "test_validate":
        [{
            "testcase": 'Test validation for valid PNG file',
            "filename": '02_filevalidation_data/png/valid.png',
            "mimetype": 'image/png',
            "formatVersion": '',
            "expected_result": {
                "status": 0,
                "stdout": ['OK'],
                "stderr": ''
            }
        },
            {
            "testcase": 'Test validation for invalid PNG file',
            "filename": '02_filevalidation_data/png/invalid.png',
            "mimetype": 'image/png',
            "formatVersion": '',
            "expected_result": {
                "status": 2,
                "stdout": ['ERROR'],
                "stderr": ['Validator returned error']
            }
        }]
    }

    def test_validate(self, testcase, filename, mimetype, formatVersion,
                      expected_result):

        filename = os.path.join(testcommon.settings.TESTDATADIR, filename)

        for testcase in self.testcases["test_validate"]:

            print "%s: %s" % (testcase["testcase"], testcase["filename"])

            testcase["filename"] = os.path.join(testcommon.settings.TESTDATADIR,
                                                testcase["filename"])
            val = ipt.validator.plugin.pngcheck.Pngcheck(testcase["mimetype"],
                                                         testcase[
                                                             "formatVersion"],
                                                         testcase["filename"])

            (status, stdout, stderr) = val.validate()

            if testcase["expected_result"]["status"] == 0:
                assert testcase["expected_result"]["status"] == status
            else:
                assert testcase["expected_result"]["status"] != 0

            for match_string in testcase["expected_result"]["stdout"]:
                stdout = stdout.decode('utf-8')
                assert match_string in stdout

            for match_string in testcase["expected_result"]["stderr"]:
                stderr = stderr.decode('utf-8')
                assert match_string in stderr

            if "profile" in testcase["expected_result"]:
                assert val.check_profile(
                    testcase["expected_result"]["profile"]) == None

            del val

        return None
