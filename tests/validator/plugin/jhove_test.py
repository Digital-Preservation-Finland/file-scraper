# Common boilerplate
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

import re
import pytest
import testcommon.settings
from testcommon.casegenerator import pytest_generate_tests

# Module to test
import validator.plugin.jhove

#VALIDATORS_CONFIG_FILENAME = os.path.join(testcommon.settings.SHAREDIR,
#                                          'validators/validators.json')

class TestJhoveFilevalidator:

    testcases = {
        "test_validate":
        [{
            "testcase": 'Test validation for valid JPEG file',
            "filename": 'test-sips/CSC_test001/kuvat/P1020137.JPG',
            "mimetype": 'image/jpeg',
            "formatVersion": '',
            "expected_result": {
                "status": 0,
                "stdout": ['Status: Well-Formed and valid'],
                "stderr": ''
            }
         },
         {
            "testcase": 'Test validation for valid PDF file',
            "filename": 'test-sips/CSC_test004/fd2009-00002919-pdf001.pdf',
            "mimetype": 'application/pdf',
            "formatVersion": '1.4',
            "expected_result": {
                "status": 0,
                "stdout": ['Status: Well-Formed and valid'],
                "stderr": ''
            }
         },
         {
            "testcase": 'Test validation for valid JP2 file',
            "filename": '../testfiles/kuvat/valid.jp2',
            "mimetype": 'image/jp2',
                "formatVersion": '',
                "expected_result": {
                "status": 0,
                "stdout": ['Status: Well-Formed and valid'],
                "stderr": ''
            }
         }]
    }
    


    def test_validate(self, testcase, filename, mimetype, formatVersion,
                      expected_result):
        
        filename = os.path.join(testcommon.settings.TESTDATADIR, filename)
        
        val = validator.plugin.jhove.Jhove()
        

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