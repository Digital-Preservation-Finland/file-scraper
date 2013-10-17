# Common boilerplate
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
import pytest
import testcommon.settings
from testcommon.casegenerator import pytest_generate_tests

# Module to test
import validator.plugin.schematron

# Other imports
import shutil
import tempfile

SHARE_PATH = os.path.abspath(os.path.os.path.join(
                             os.path.dirname(__file__),
                             '../../../',
                             'include/share'))

SCHEMATRON_PATH = os.path.join(SHARE_PATH, 'kdk-schematron')
TESTROOT = os.path.join(
    os.path.abspath(os.path.dirname(__file__)), '../../',
    'data/test-sips')


class TestSchematronValidator:

    testcases = {
        "test_schematron_to_xslt": [
            {"casename": "Good schematron file - mets_internal.sch",
             "filename": os.path.join(SCHEMATRON_PATH, "mets_internal.sch")},
            {"casename": "Good schematron file - mets_mdtype.sch",
             "filename": os.path.join(SCHEMATRON_PATH, "mets_mdtype.sch")},
            {"casename": "Good schematron file - mets_mix.sch",
             "filename": os.path.join(SCHEMATRON_PATH, "mets_mix.sch")},
        ],
        "test_validate_file": [
            {"casename": "Kervinen",
             "filename": "fd2009-00002919-preservation/mets.xml",
             "expect_errors": [False, False, False]}
        ]
    }

       #
       # "test_validate_file": [
      #      {"casename": "Good METS document",
      #       "filename": "CSC_test001/mets.xml",
      #       "expect_errors" : [False, False, False] },
      #      {"casename": "Good METS document",
      #       "filename": "metsrights-error/mets.xml",
      #       "expect_errors" : [False, True, False] },
      #      {"casename" : "Kervinen",
             #
      #       "filename" : "fd2009-00002919-preservation/mets.xml",
      #       "expect_errors" : [False, False, False]}
             #
      #  ]
   # }
    def file_contains_string(self, filename, search_strings):

        f = open(filename)
        search_results = {}

        for search_string in search_strings:
            search_results[search_string] = False

        for line in f:
            for search_string in search_strings:
                if line.find(search_string) >= 0:
                    search_results[search_string] = True

        f.close()

        result = True
        for search_string, search_result in search_results.iteritems():
            assert search_result, "Text '%s' not found from template %s" % (
                search_string, filename)

    def file_is_stylesheet(self, filename):

        search_strings = [
            '<axsl:stylesheet',
            '<axsl:template',
            '</axsl:template></axsl:stylesheet>'
        ]

        self.file_contains_string(filename, search_strings)

    def test_schematron_to_xslt(self, casename, filename):

        temppath = tempfile.mkdtemp()

        try:

            validate = validator.plugin.schematron.XSLT()
            validator.cachepath = temppath
            validator.sharepath = SHARE_PATH

            xslt_filename = validate.schematron_to_xslt(filename)

            self.file_is_stylesheet(xslt_filename)

        except Exception as e:
            raise e
        finally:
            shutil.rmtree(temppath)

    def svlr_has_errors(self, svrl_text):

        if svrl_text.find('<svr') == -1:
            print "Not a valid schematron validation result SVRL"
            return True

        start_tag = '<svrl:failed-assert'
        end_tag = '</svrl:failed-assert'

        result = False
        end_position = 0

        while True:
            start_position = svrl_text.find(start_tag, end_position +
                                            len(end_tag))
            if start_position == -1:
                    break

            end_position = svrl_text.find(end_tag, start_position)

            print "------ Found error in validated file"
            print svrl_text[start_position:end_position + len(end_tag)]
            print "------"

            result = True

        return result

    def test_validate_file(self, casename, filename, expect_errors):
        temppath = tempfile.mkdtemp()

        try:

            validate = validator.plugin.schematron.XSLT()
            validator.cachepath = temppath
            validator.sharepath = SHARE_PATH

            schemas = ["mets_internal.sch", "mets_mdtype.sch", "mets_mix.sch"]

            i = 0
            for schema in schemas:

                mets_path = os.path.join(TESTROOT, filename)
                schema_path = os.path.join(SCHEMATRON_PATH, schema)

                result = validate.validate_file(schema_path, mets_path)

                print result

                if expect_errors[i]:
                    assert self.svlr_has_errors(result.messages) == True, \
                        "Expected errors, but validator found no errors " +\
                        "[%s]" % (schema)
                else:
                    assert self.svlr_has_errors(result.messages) == False, \
                        "Expected no errors, but validator found errors " +\
                        "[%s]" % (schema)
                i = i + 1

        finally:
            shutil.rmtree(temppath)
