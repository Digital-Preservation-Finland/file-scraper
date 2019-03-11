"""Tests for Csv scraper"""

import os
import lxml.etree
from tempfile import NamedTemporaryFile

from dpres_scraper.scrapers.csv_scraper import Csv

PDF_PATH = os.path.join(
    'tests/data/application_pdf/valid_1.4.pdf')

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


def run_scraper(csv_text, mimetype='text/csv'):
    """Write test data and run csv scraping for the file"""

    with NamedTemporaryFile(delete=False) as outfile:

        try:
            outfile.write(csv_text)
            outfile.close()

            scraper = Csv(outfile.name, mimetype)
            scraper.scrape_file()
        finally:
            os.unlink(outfile.name)

    return scraper


def test_valid_no_header():
    """Test the scraper with valid data from Wikipedia's CSV article"""

    scraper = run_scraper(VALID_CSV)

    assert scraper.well_formed, scraper.messages() + scraper.errors()
    assert "successfully" in scraper.messages()
    assert scraper.errors() == ""


def test_valid_with_header():
    """Test valid CSV with headers"""

    scraper = run_scraper(VALID_WITH_HEADER)

    assert scraper.well_formed, scraper.messages() + scraper.errors()
    assert "successfully" in scraper.messages()
    assert scraper.errors() == ""

"""
def test_single_field_csv():
    Test CSV which contains only single field.

    Here we provide original data, but use different field separator

    
    addml = {
        "charset": "UTF-8",
        "separator": "CR+LF",
        "delimiter": ";",
        "header_fields": ["year,brand,model,detail,other"]}

    scraper = run_scraper(VALID_WITH_HEADER, addml)

    assert scraper.well_formed, scraper.messages() + scraper.errors()
    assert "successfully" in scraper.messages()
    assert scraper.errors() == ""
"""

def test_pdf_as_csv():
    """Test CSV scraper with PDF files"""

    scraper = run_scraper(open(PDF_PATH).read())

    assert not scraper.well_formed, scraper.messages() + scraper.errors()
    assert "successfully" not in scraper.messages()
    assert len(scraper.errors()) > 0


def test_missing_end_quote():
    """Test missing end quote"""

    scraper = run_scraper(MISSING_END_QUOTE)

    assert not scraper.well_formed, scraper.messages() + scraper.errors()
    assert "successfully" not in scraper.messages()
    assert len(scraper.errors()) > 0

"""
def test_invalid_field_delimiter():
    Test different field separator than defined in addml

    addml = {
        "charset": "UTF-8",
        "separator": "CR+LF",
        "delimiter": ";",
        "header_fields": ["year", "brand", "model", "detail", "other"]}

    scraper = run_scraper(VALID_WITH_HEADER, addml)

    assert not scraper.well_formed, scraper.messages() + scraper.errors()
    assert "CSV scraping error: field counts" in scraper.errors()
    assert "successfully" not in scraper.messages()
    assert len(scraper.errors()) > 0
"""
