"""Tests for PythonCsv validator"""

import os
import lxml.etree
from tempfile import NamedTemporaryFile

from ipt.validator.csv_validator import PythonCsv
from ipt.addml.addml import to_dict

PDF_PATH = os.path.join(
    'tests/data/02_filevalidation_data/pdf_1_4/sample_1_4.pdf')

ADDML_PATH = os.path.join('tests', 'data', 'addml', 'addml.xml')

VALID_CSV = (
    '''1997,Ford,E350,"ac, abs, moon",3000.00\n'''
    '''1999,Chevy,"Venture ""Extended Edition""","",4900.00\n'''
    '''1999,Chevy,"Venture ""Extended Edition, Very Large""",,5000.00\n'''
    '''1996,Jeep,Grand Cherokee,"MUST SELL!\n'''
    '''air, moon roof, loaded",4799.00\n''')

VALID_WITH_HEADER = \
    'year,brand,model,detail,other\n' + VALID_CSV

MISSING_END_QUOTE = VALID_CSV + \
    '1999,Chevy,"Venture ""Extended Edition"","",4900.00\n'

DEFAULT_FORMAT = {
    "mimetype": "text/csv",
    "version": "",
    "charset": "UTF-8"}

DEFAULT_ADDML = {
    "charset": "UTF-8",
    "separator": "CR+LF",
    "delimiter": ",",
    "header_fields": ""}


def run_validator(csv_text, addml=None, file_format=None, fileinfo=None):
    """Write test data and run csv validation for the file"""

    if addml is None:
        addml = DEFAULT_ADDML

    if file_format is None:
        file_format = DEFAULT_FORMAT

    with NamedTemporaryFile(delete=False) as outfile:

        try:
            outfile.write(csv_text)
            outfile.close()

            if fileinfo is None:
                fileinfo = {
                    "format": file_format,
                    "addml": addml
                }

            fileinfo["filename"] = outfile.name

            validator = PythonCsv(fileinfo)
            validator.validate()
        finally:
            os.unlink(outfile.name)

    return validator


def test_valid_created_addml():
    """Test that CSV validator can handle the ADDML given from addml.py"""
    addml_tree = lxml.etree.parse(ADDML_PATH)
    addml = to_dict(addml_tree)
    validator = run_validator("name; email", addml['addml'])

    assert validator.is_valid, validator.messages() + validator.errors()
    assert "CSV validation OK" in validator.messages()
    assert validator.errors() == ""


def test_valid_no_header():
    """Test the validator with valid data from Wikipedia's CSV article"""

    validator = run_validator(VALID_CSV)

    assert validator.is_valid, validator.messages() + validator.errors()
    assert "CSV validation OK" in validator.messages()
    assert validator.errors() == ""


def test_valid_with_header():
    """Test valid CSV with headers"""

    addml = {
        "charset": "UTF-8",
        "separator": "CR+LF",
        "delimiter": ",",
        "header_fields": ["year", "brand", "model", "detail", "other"]
    }

    validator = run_validator(VALID_WITH_HEADER, addml)

    assert validator.is_valid, validator.messages() + validator.errors()
    assert "CSV validation OK" in validator.messages()
    assert validator.errors() == ""


def test_single_field_csv():
    """Test CSV which contains only single field.

    Here we provide original data, but use different field separator

    """
    addml = {
        "charset": "UTF-8",
        "separator": "CR+LF",
        "delimiter": ";",
        "header_fields": ["year,brand,model,detail,other"]}

    validator = run_validator(VALID_WITH_HEADER, addml)

    assert validator.is_valid, validator.messages() + validator.errors()
    assert "CSV validation OK" in validator.messages()
    assert validator.errors() == ""


def test_missing_header():
    """Test in invalid csv validation"""

    addml = {
        "charset": "UTF-8",
        "separator": "CR+LF",
        "delimiter": ",",
        "header_fields": ["MISSING HEADER"]}

    validator = run_validator(VALID_WITH_HEADER, addml)

    assert not validator.is_valid, validator.messages() + validator.errors()
    assert "CSV validation OK" not in validator.messages()
    assert "CSV validation error: field counts" in validator.errors()


def test_pdf_as_csv():
    """Test CSV validator with PDF files"""

    validator = run_validator(open(PDF_PATH).read())

    assert not validator.is_valid, validator.messages() + validator.errors()
    assert "CSV validation OK" not in validator.messages()
    assert len(validator.errors()) > 0


def test_missing_end_quote():
    """Test missing end quote"""

    validator = run_validator(MISSING_END_QUOTE)

    assert not validator.is_valid, validator.messages() + validator.errors()
    assert "CSV validation OK" not in validator.messages()
    assert len(validator.errors()) > 0


def test_invalid_field_delimiter():
    """Test different field separator than defined in addml"""

    addml = {
        "charset": "UTF-8",
        "separator": "CR+LF",
        "delimiter": ";",
        "header_fields": ["year", "brand", "model", "detail", "other"]}

    validator = run_validator(VALID_WITH_HEADER, addml)

    assert not validator.is_valid, validator.messages() + validator.errors()
    assert "CSV validation error: field counts" in validator.errors()
    assert "CSV validation OK" not in validator.messages()
    assert len(validator.errors()) > 0


def test_invalid_missing_addml_fileinfo():
    """Test valid CSV without providing ADDML data in fileinfo"""

    addml = {
        "charset": "UTF-8",
        "separator": "CR+LF",
        "delimiter": ",",
        "header_fields": ["year", "brand", "model", "detail", "other"]
    }
    fileinfo = {
        "format": DEFAULT_FORMAT
    }

    validator = run_validator(VALID_WITH_HEADER, addml, fileinfo=fileinfo)

    assert not validator.is_valid, validator.messages() + validator.errors()
    assert "ADDML data was expected, but not found" in validator.errors()
    assert "CSV validation OK" not in validator.messages()
