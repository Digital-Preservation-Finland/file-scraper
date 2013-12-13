# Common boilerplate
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

import re
import json
import pytest
import testcommon.settings

# Module to test
import validator.plugin.libxml

PROJECTDIR = testcommon.settings.PROJECTDIR

TESTDATADIR_BASE = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                '../../data'))

TESTDATADIR = os.path.abspath(os.path.join(TESTDATADIR_BASE,
                                           '02_filevalidation_data'))

CATALOGPATH = os.path.join(testcommon.settings.SHAREDIR, 'schema/catalog-local.xml')

class TestXmllibFilevalidator:

    def test_validate(self):


        testcasefile = os.path.join(PROJECTDIR, TESTDATADIR,
                                    'xmllib_testcases.json')
        print "\nLoading test configuration from %s\n" % testcasefile
                            
        json_data = open(testcasefile)
        testcases = json.load(json_data)
        json_data.close()
        
        
        for testcase in testcases["test_validate"]:
            
            print "%s: %s" % (testcase["testcase"], testcase["filename"])

            testcase["filename"] = os.path.join(testcommon.settings.TESTDATADIR,
                                                testcase["filename"])
            val = validator.plugin.libxml.Libxml(testcase["mimetype"],
                                               testcase["formatVersion"],
                                               testcase["filename"])        

            val.addCatalog(CATALOGPATH)
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
    
            del val
        
        return None