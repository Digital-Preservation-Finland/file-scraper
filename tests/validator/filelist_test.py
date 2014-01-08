# Common boilerplate
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(
		os.path.dirname(__file__), '..')))
import pytest
import testcommon.settings
import json

# Module to test
import validator.filelist
import mets.parser
import mets.manifest

import pas_scripts.check_sip_digital_objects
import validator.plugin.mockup

# Other imports
import random
import string
import re
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

        for mimetype, test_configs in testcases.iteritems():

            print "Testing files with mimetype: %s" % mimetype

            for test_config in test_configs:
                
                manifest = mets.manifest.File(os.path.join(
                                                TESTDATADIR,
                                                test_config["path"],
                                                'MANIFEST'))

                filelist = manifest.get_filelist()

                validate = validator.filelist.Validator(
                                base_path=os.path.join(TESTDATADIR, mimetype))

                validate.load_config(TEST_CONFIG_FILENAME)

                (returns, reports, errors, validators) = validate.validate_files(filelist)
                
                ret = 0
                for r in returns:
                    if r != 0: ret = r
                
                report = "\n".join(reports)
                error = "\n".join(errors)

                for match_stdout in test_config["match_stdout"]:
                    #match = re.match('(?s).*%s' % match_stdout, report) != None
                    #message = ''.join(['---%s--- ' % report,
                    #                   "No match for: '%s'" % match_stdout])
                    assert match_stdout in report
                    #match, message

                for match_stderr in test_config["match_stderr"]:
                    #match = re.match('(?s).*%s' % match_stderr, report) != None
                    #message = ''.join(['---%s--- ' % error,
                    #                   "No match for: '%s'" % match_stderr])
                    assert match_stderr in report

                assert ret == test_config["exitstatus"]
                
    def test_validate_file(self):
        fileinfo = validator.filelist.FileInfo()
        fileinfo.format_mimetype = "application/pdf"
        fileinfo.filename = "abc"
        
        validator_path = "validator.plugin.mockup.ValidatorMockup"
        validate = validator.filelist.Validator() 

        # Generate expected return values randomly
        random_int = 50
        while random_int < 50:
            random_string = ''.join(random.choice(string.lowercase) for i in range(random_int))        
            return_values = ( random_int, random_string, random_string*2 )
            assert validate.validate_file(fileinfo, validator_path, return_values ) == return_values
            random_int = random.randint(0,100)

    def test_get_class_instance_by_name(self):
        validate = validator.filelist.Validator()
        instance = validate.get_class_instance_by_name("json.JSONDecoder", None)
        assert isinstance( instance, json.JSONDecoder)