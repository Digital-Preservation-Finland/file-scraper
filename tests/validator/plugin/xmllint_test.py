# Common boilerplate
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
import testcommon.settings
from testcommon.casegenerator import pytest_generate_tests

# Module to test
import ipt.validator.plugin.xmllint


ROOTPATH = os.path.abspath(os.path.join(
    os.path.dirname(__file__),
    '../../../'))
SHAREPATH = os.path.join(ROOTPATH, 'include/share')
OBJECT_CATALOGPATH = os.path.join(
    SHAREPATH,
    'xmlobjectcatalog/catalog-local.xml')
SCHEMAPATH = os.path.join(SHAREPATH, 'schema/mets/mets.xsd')


class TestXmllintValidation:

    testcases = {
        "test_validation": [
            {"testcase": {
             "name": "Test XSD validation with KDK METS schema 1",
                "filepath": '06_mets_validation/sips/CSC_test001/mets.xml',
                "catalog": OBJECT_CATALOGPATH,
                "schema": SCHEMAPATH

             },
             "expected": {
                 "returncode": 0,
                 "stdout_has_errors": False,
                 "stderr_has_errors": False,
            }
            },
            {"testcase": {
             "name": "Test XSD validation with KDK METS schema 2",
                "filepath":
             '06_mets_validation/sips/fd2009-00002919-preservation/mets.xml',
                "catalog": OBJECT_CATALOGPATH,
                "schema": SCHEMAPATH
             },
             "expected": {
                 "returncode": 0,
                 "stdout_has_errors": False,
                 "stderr_has_errors": False,
            }
            },
            {"testcase": {
             "name": "Test XSD validation with schema from object catalog",
                "filepath":
             '02_filevalidation_data/xml/catalog_schema_valid.xml',
                "catalog": OBJECT_CATALOGPATH
             },
             "expected": {
                 "returncode": 0,
                 "stdout_has_errors": False,
                 "stderr_has_errors": False,
            }
            },
            {"testcase": {
             "name": "Test XSD validation with non existing schema",
                "filepath":
             '02_filevalidation_data/xml/catalog_schema_invalid.xml',
                "catalog": OBJECT_CATALOGPATH
             },
             "expected": {
                 "returncode": 3,
                 "stdout_has_errors": False,
                 "stderr_has_errors": True,
            }
            },
            {"testcase": {
             "name": "Test XSD validation with valid XML file",
                "filepath": '02_filevalidation_data/xml/valid_xsd.xml',
                "catalog": OBJECT_CATALOGPATH
             },
             "expected": {
                 "returncode": 0,
                 "stdout_has_errors": False,
                 "stderr_has_errors": False,
            }
            },
            {"testcase": {
             "name": "Test XSD validation with invalid XML file",
                "filepath": '02_filevalidation_data/xml/invalid_xsd.xml',
                "catalog": OBJECT_CATALOGPATH
             },
             "expected": {
                 "returncode": 3,
                 "stdout_has_errors": False,
                 "stderr_has_errors": True,
            }
            },
            {"testcase": {
             "name": "Test validation with well-formed XML file",
                "filepath": '02_filevalidation_data/xml/valid_wellformed.xml'
             },
             "expected": {
                 "returncode": 0,
                 "stdout_has_errors": False,
                 "stderr_has_errors": False,
            }
            },
            {"testcase": {
             "name": "Test validation with not well-formed XML file",
                "filepath": '02_filevalidation_data/xml/invalid_wellformed.xml'
             },
             "expected": {
                 "returncode": 1,
                 "stdout_has_errors": False,
                 "stderr_has_errors": True,
            }
            },
            {"testcase": {
             "name": "Test DTD validation with valid XML file",
                "filepath": '02_filevalidation_data/xml/valid_dtd.xml'
             },
             "expected": {
                 "returncode": 0,
                 "stdout_has_errors": False,
                 "stderr_has_errors": False,
            }
            },
            {"testcase": {
             "name": "Test DTD validation with invalid XML file",
                "filepath": '02_filevalidation_data/xml/invalid_dtd.xml'
             },
             "expected": {
                 "returncode": 4,
                 "stdout_has_errors": False,
                 "stderr_has_errors": True,
            }
            },
            {"testcase": {
             "name": "Test mets not in sip root",
                "filepath": "06_mets_validation/sips/mets_not_in_root/mets.xml",
                "catalog": OBJECT_CATALOGPATH,
                "schema": SCHEMAPATH

             },
             "expected": {
                 "returncode": 117,
                 "stdout_has_errors": False,
                 "stderr_has_errors": False,
            }
            }
        ]
    }

    def test_validation(self, testcase, expected):
        file_path = os.path.join(
            testcommon.settings.TESTDATADIR, testcase["filepath"])

        validate = ipt.validator.plugin.xmllint.Xmllint(
            "text/xml",
            "1.0",
            file_path)

        if "catalog" in testcase:
            validate.set_catalog(testcase["catalog"])
        if "schema" in testcase:
            validate.add_schema(testcase["schema"])

        (returncode, messages, errors) = validate.validate()

        assert returncode == expected["returncode"], '\n'.join([
            'stdout:', validate.stdout, 'stderr:', validate.stderr])
        assert self.output_has_error(
            messages) == expected["stdout_has_errors"]
        assert self.output_has_error(
            errors) == expected["stderr_has_errors"]

    def output_has_error(self, lines):
        if "failed" in lines or "error" in lines:
            return True

        return False
