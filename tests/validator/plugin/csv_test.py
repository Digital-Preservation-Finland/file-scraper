"""Tests for PythonCsv validator"""

import os
from tempfile import NamedTemporaryFile

from ipt.validator.csv_validator import PythonCsv

PDF_PATH = os.path.join(
    'tests/data/02_filevalidation_data/pdf_1_4/sample_1_4.pdf')

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


def run_validator(csv_text, addml=None, file_format=None):
    """Write test data and run csv validation for the file"""

    if addml is None:
        addml = DEFAULT_ADDML

    if file_format is None:
        file_format = DEFAULT_FORMAT

    with NamedTemporaryFile(delete=False) as outfile:

        try:
            outfile.write(csv_text)
            outfile.close()

            fileinfo = {
                "filename": outfile.name,
                "format": file_format,
                "addml": addml
            }

            validator = PythonCsv(fileinfo)
            validator.validate()
        finally:
            os.unlink(outfile.name)

    return validator


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
    assert "no header at first line" in validator.errors()


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
    assert 'no header at first line' in validator.errors()
    assert "CSV validation OK" not in validator.messages()
    assert len(validator.errors()) > 0
