"""Test for python CSV validation"""
import os
import pytest

from tempfile import NamedTemporaryFile

from ipt.validator.csv_validator import PythonCsv

JPEG_PATH = os.path.join('tests/data/test-sips/CSC_test004/'
                         '/access_img/img0008-access.jpg')


VALID_CSV = ('''1997,Ford,E350,"ac, abs, moon",3000.00\n'''
'''1999,Chevy,"Venture ""Extended Edition""","",4900.00\n'''
'''1999,Chevy,"Venture ""Extended Edition, Very Large""",,5000.00\n'''
'''1996,Jeep,Grand Cherokee,"MUST SELL!\nair, moon roof, loaded",4799.00\n''')

VALID_WITH_HEADER = \
    'year,brand,model,detail,other\n' + VALID_CSV


INVALID_CSV = VALID_CSV + \
    '1999,Chevy,"Venture ""Extended Edition"","",4900.00\n'


def write_testdata(infile, data=VALID_CSV):

    infile.write(data)
    infile.close()
    return infile.name


def test_validate_success_wikipedia():
    """Test the validator with valid data from Wikipedia's CSV article"""

    with NamedTemporaryFile(delete=False) as csv_file:
        fileinfo = {
            "filename": write_testdata(csv_file, VALID_CSV),
            "format": {
                "mimetype": "text/csv",
                "version": "",
                "charset": "UTF-8"
            },
            "addml": {
                "charset": "UTF-8",
                "separator": "CR+LF",
                "delimiter": ";",
                "header_fields": ""
            }
        }

        validator = PythonCsv(fileinfo)
        validator.validate()

        assert validator.is_valid, validator.messages() + validator.errors()
        assert "CSV validation OK" in validator.messages()
        assert validator.errors() == ""

    with NamedTemporaryFile(delete=False) as csv_file:
        fileinfo = {
            "filename": write_testdata(csv_file, VALID_WITH_HEADER),
            "format": {
                "mimetype": "text/csv",
                "version": "",
                "charset": "UTF-8"
            },
            "addml": {
                "charset": "UTF-8",
                "separator": "CR+LF",
                "delimiter": ";",
                "header_fields": ["year", "brand", "model", "detail", "other"]
            }
        }

        validator = PythonCsv(fileinfo)
        validator.validate()

        assert validator.is_valid
        assert "CSV validation OK" in validator.messages()
        assert validator.errors() == ""


def test_validate_failure():

    with NamedTemporaryFile(delete=False) as csv_file:
        fileinfo = {
            "filename": write_testdata(csv_file, VALID_WITH_HEADER),
            "format": {
                "mimetype": "text/csv",
                "version": "",
                "charset": "UTF-8"
            },
            "addml": {
                "charset": "UTF-8",
                "separator": "CR+LF",
                "delimiter": ";",
                "header_fields": ["MISSING HEADER"]
            }
        }

        validator = PythonCsv(fileinfo)
        validator.validate()

        assert not validator.is_valid
        assert "CSV validation OK" not in validator.messages()
        assert "no header at first line" in validator.errors()

    with NamedTemporaryFile(delete=False) as csv_file:
        fileinfo = {
            "filename": JPEG_PATH,
            "format": {
                "mimetype": "text/csv",
                "version": "",
                "charset": "UTF-8"
            },
            "addml": {
                "charset": "UTF-8",
                "separator": "CR+LF",
                "delimiter": ";",
                "header_fields": ""
            }
        }

        validator = PythonCsv(fileinfo)
        validator.validate()

        assert not validator.is_valid
        assert len(validator.errors()) != 0
        assert "CSV validation OK" not in validator.messages(), validator.messages() + validator.errors()

    with NamedTemporaryFile(delete=False) as csv_file:
        fileinfo = {
            "filename": write_testdata(csv_file, INVALID_CSV),
            "format": {
                "mimetype": "text/csv",
                "version": "",
                "charset": "UTF-8"
            },
            "addml": {
                "charset": "UTF-8",
                "separator": "CR+LF",
                "delimiter": ";",
                "header_fields": ""
            }
        }

        validator = PythonCsv(fileinfo)
        validator.validate()

        assert not validator.is_valid
        assert "CSV validation OK" not in validator.messages()
        assert len(validator.errors())
