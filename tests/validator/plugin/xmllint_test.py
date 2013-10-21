# Common boilerplate
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
import pytest
import testcommon.settings
from testcommon.casegenerator import pytest_generate_tests

# Module to test
import validator.plugin.xmllint

# Other imports
import subprocess

ROOTPATH = os.path.abspath(os.path.join(
    os.path.dirname(__file__),
    '../../../'))

SHAREPATH = os.path.join(ROOTPATH, 'include/share')

CATALOGPATH = os.path.join(SHAREPATH, 'schema/catalog-local.xml')
SCHEMAPATH = os.path.join(SHAREPATH, 'schema/mets/mets.xsd')


class TestMetsValidation:

    testcases = {
        "test_mets_validation": [
            {"testcase":   {
             "name": "CSC_test001",
                "metspath": '06_mets_validation/sips/CSC_test001/mets.xml'
             },
             "expected":    {
                 "returncode": 0,
                 "stdout_has_errors": False,
                 "stderr_has_errors": False,
             }
             },
            {"testcase":   {
             "name": "fd2009-00002919-preservation",
                "metspath": '06_mets_validation/sips/fd2009-00002919-preservation/mets.xml'
             },
             "expected":    {
                 "returncode": 0,
                 "stdout_has_errors": False,
                 "stderr_has_errors": False,
             }
             }

        ]
    }

    def output_has_error(self, lines):

        for line in lines:
            if line.find("failed") >= 0:
                return True
            if line.find("error") >= 0:
                return True

        return False

    def test_mets_validation(self, testcase, expected):

        validate = validator.plugin.xmllint.XSDCatalog(CATALOGPATH, SCHEMAPATH)
        print "TESTDATADIR", testcommon.settings.TESTDATADIR
        mets_path = os.path.join(
            testcommon.settings.TESTDATADIR, testcase["metspath"])
        result = validate.validate_file(mets_path)
        print "mets_path", mets_path
        print result.returncode, result.messages, result.errors

        assert result.returncode == expected["returncode"]
        assert self.output_has_error(
            result.messages) == expected["stdout_has_errors"]
        assert self.output_has_error(
            result.errors) == expected["stderr_has_errors"]
