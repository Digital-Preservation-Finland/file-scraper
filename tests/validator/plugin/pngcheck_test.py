# Common boilerplate
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

import re
import pytest
import testcommon.settings
from testcommon.casegenerator import pytest_generate_tests

# Module to test
import validator.plugin.pngcheck

#VALIDATORS_CONFIG_FILENAME = os.path.join(testcommon.settings.SHAREDIR,
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
                "stderr": ''
            }
         }]
    }
    

    def test_validate(self, testcase, filename, mimetype, formatVersion,
                      expected_result):
        
        filename = os.path.join(testcommon.settings.TESTDATADIR, filename)
        
        val = validator.plugin.pngcheck.Pngcheck()
        

        (status, stdout, stderr) = val.validate(mimetype,
                                               formatVersion,
                                               filename)

        assert expected_result["status"] == status
        
        for match_string in expected_result["stdout"]:
            message = "\n".join(["got:", stdout, "expected:", match_string])
            assert re.match('(?s).*' + match_string, stdout), message
        
        for match_string in expected_result["stderr"]:
            message = "\n".join(["got:", stderr, "expected:", match_string])
            assert re.match('(?s).*' + match_string, stderr), message
        
        return None