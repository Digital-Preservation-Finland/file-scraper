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

#import pas_scripts.check_sip_digital_objects
#import pas_scripts.jhove_pas
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
    	testcasefile = os.path.join(PROJECTDIR, TESTDATADIR, 'testcases.json')

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

                (ret, report, errors) = validate.validate_files(filelist)

                for match_stdout in test_config["match_stdout"]:
                    match = re.match('(?s).*%s' % match_stdout, report) != None
                    message = ''.join(['---%s--- ' % report,
                                       "No match for: '%s'" % match_stdout]) 
                    assert match, message

                for match_stderr in test_config["match_stderr"]:
                    match = re.match('(?s).*%s' % match_stderr, report) != None
                    message = ''.join(['---%s--- ' % errors,
                                       "No match for: '%s'" % match_stderr]) 
                    assert match, message

                assert ret == test_config["exitstatus"]

    def test_get_class_instance_by_name(self):
        validate = validator.filelist.Validator()
        instance = validate.get_class_instance_by_name("json.JSONDecoder", None)
        assert isinstance( instance, json.JSONDecoder)  
                
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

class TestCommandLineTools:

    @pytest.mark.parametrize(("input", "expected"), [
        ({
            "filename":"pdf_1_4/sample_1_4.pdf",
            "version":"1.4",
            "mimetype":"application/pdf"
        }, {
            "stdout":["Status: Well-Formed and valid"],
            "stderr":[],
            "returncode": 0
        }),
        ({
            "filename":"pdf_1_4/sample_invalid_1_4.pdf",
            "version":"1.4",
            "mimetype":"application/pdf"
        }, {
            "stdout":["Not well-formed"],
            "stderr":[],
            "returncode": 1
        }),

    ])

##    def test_jhove_pas(self, input, expected):
##        filename = os.path.join(TESTDATADIR, input["filename"])
        #TODO: Remove this!
        #command = "jhove-pas -t %s -v %s '%s'" % (input["mimetype"],
        #                                         input["version"],
        #                                         filename)

        #options = {
        #        "mimetype":input["mimetype"],
        #        "formatversion":input["version"]
        #        }

        #arguments = [filename]

##        arguments = ["-t%s" % input["mimetype"],
##                     "-v%s" % input["version"],
##                     filename]

##        self.do(pas_scripts.jhove_pas.main, arguments, expected)

    @pytest.mark.parametrize(("input", "expected"), [
        ({
            "filename":"CSC_test001",
        }, {
            "stdout":[""],
            "stderr":[""],
            "returncode": 0
        }),
        ({
            "filename":"CSC_test002",
        }, {
            "stdout":[""],
            "stderr":[""],
            "returncode": 0
        }),
        ({
            "filename":"fd2009-00002919-preservation",
        }, {
            "stdout":["Status: Well-Formed and valid"],
            "stderr":["No validator for mimetype\:image/jpeg version\:1.01",
                      "No validator for mimetype:text/xml version:ALTO " +
                      "schema Version 1.4"],
            "returncode": 1
        }),

    ])

##    def test_check_sip_digital_objects(self, input, expected):

##        filename = os.path.join(TESTDATADIR_BASE, 'test-sips',
##                                input["filename"], 'mets.xml')

##        configfile =  os.path.abspath(os.path.join(PROJECTDIR, '../' 'include/share',
##                'validators', 'validators.json'))

        # TODO: Remove this!
        #command = "check-sip-digital-objects -c'%s' '%s'" % (
        #                            os.path.join(PROJECTDIR, '../../../'
        #                                         'include/share',
        #                                         'validators',
        #                                         'validators.json'),
        ##                             filename)

        #options = {
        #    'config_filename': os.path.join(PROJECTDIR,
        #                                    '../../../'
        #                                    'include/share',
        #                                    'validators',
        #                                    'validators.json')}
        #arguments = [filename]

        # TODO: Remove this!
##        arguments = [
##                "-c%s" % configfile,
##                "%s" % filename]
        
##        self.do(pas_scripts.check_sip_digital_objects.main, arguments,
##                expected)

    def do(self, command, arguments, expected):

        # TODO: Remove this
        #cmd = ["PATH=%s/../bin:$PATH ; %s" % (PROJECTDIR, command)]
        #proc = subprocess.Popen(cmd, stdout=subprocess.PIPE,
        #                        stderr=subprocess.PIPE, shell=True)
        #(stdout, stderr) = proc.communicate()
        #returncode = proc.returncode
          
        (returncode, stdout, stderr) = testcommon.shell.run_main(
                command, arguments)

        print stdout, stderr, returncode

        function_name = "%s.%s" % (command.__module__, command.func_name)
        for match_string in expected["stdout"]:
            message = "\n".join(["got:", stdout, "expected:", match_string,
                "function:", function_name])
            assert re.match('(?s).*' + match_string, stdout), message

        for match_string in expected["stderr"]:
            message = "\n".join(["got:", stderr, "expected:", match_string,
                "function:", function_name])
            assert re.match('(?s).*' + match_string, stderr), message

        message = "\n".join(["got:", str(returncode), "expected:",
            str(expected["returncode"]), "stdout:", stdout, "stderr:",
            stderr, "function:", function_name])
        assert returncode == expected["returncode"], message




