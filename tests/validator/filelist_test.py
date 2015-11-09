# Common boilerplate
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(
                os.path.dirname(__file__), '..')))

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

    def test_run_tests(self):
        testcasefile = os.path.join(PROJECTDIR, TESTDATADIR,
                                    'filelist_testcases.json')

        json_data = open(testcasefile)
        testcases = json.load(json_data)
        json_data.close()

        """These loops go through the testcases.json and validates each test
        folder(equals a sip folder). mets.xml is not in folder since its not
        relevant for this test"""

        for case in testcases:

            validate = ipt.validator.filelist.Validator(
                base_path=os.path.join(TESTDATADIR, case["path"]))

            validate.load_config(TEST_CONFIG_FILENAME)
            print "CONFIG", case
            (returns, reports, errors, validators) = validate.validate_files(
                case["filelist"])

            ret = 0
            for r in returns:
                if r != 0:
                    ret = r

            report = "\n".join(reports)
            error = "\n".join(errors)

            for match_stdout in case["match_stdout"]:
                assert match_stdout in report

            for match_stderr in case["match_stderr"]:
                assert match_stderr in report

            assert ret == case["exitstatus"]

    def test_validate_file(self):
        fileinfo = ipt.validator.filelist.FileInfo()
        fileinfo.format_mimetype = "application/pdf"
        fileinfo.filename = "abc"

        validator_path = "validator.plugin.mockup.ValidatorMockup"
        validate = ipt.validator.filelist.Validator()

        # Generate expected return values randomly
        random_int = 50
        while random_int < 50:
            random_string = ''.join(
                random.choice(string.lowercase) for i in range(random_int))
            return_values = (random_int, random_string, random_string * 2)
            assert validate.validate_file(
                fileinfo, validator_path, return_values) == return_values
            random_int = random.randint(0, 100)

    def test_get_class_instance_by_name(self):
        validate = ipt.validator.filelist.Validator()
        instance = validate.get_class_instance_by_name(
            "json.JSONDecoder", None)
        assert isinstance(instance, json.JSONDecoder)
