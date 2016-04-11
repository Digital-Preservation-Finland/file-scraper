# Common boilerplate
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

import pytest
import testcommon.settings
from testcommon.casegenerator import pytest_generate_tests

# Module to test
import ipt.validator.pngcheck

class TestPngcheckValidator:

    testcases = {
        "test_validate":
        [{
            "testcase": 'Test validation for valid PNG file',
            "fileinfo": {
                "filename": os.path.join(testcommon.settings.TESTDATADIR,
                                    '02_filevalidation_data/png/valid.png'),
                "format": {
                    "mimetype": 'image/png',
                    "version": ''
                }
            },
            "expected_result": {
                "status": 0,
                "stdout": ['OK'],
                "stderr": ''
            }
         },
         {
            "testcase": 'Test validation for invalid PNG file',
             "fileinfo": {
                "filename": os.path.join(testcommon.settings.TESTDATADIR,
                                     '02_filevalidation_data/png/invalid.png'),
                "format": {
                    "mimetype": 'image/png',
                    "version": ''
                }
             },
             "expected_result": {
                "status": 2,
                "stdout": ['ERROR'],
                "stderr": ['Validator returned error']
            }
         }]
    }

    def test_validate(self, testcase, fileinfo, expected_result):

        for testcase in self.testcases["test_validate"]:
            val = ipt.validator.pngcheck.Pngcheck(testcase["fileinfo"])

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
                assert val.check_profile( testcase["expected_result"]["profile"] ) == None


