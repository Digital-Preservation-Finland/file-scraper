"""Tests for Csv scraper"""

import os
import pytest
import lxml.etree
from tempfile import NamedTemporaryFile

from file_scraper.scrapers.csv_scraper import Csv
from tests.scrapers.common import parse_results

MIMETYPE = 'text/csv'

PDF_PATH = os.path.join(
    'tests/data/application_pdf/valid_1.4.pdf')

VALID_CSV = (
    '''1997,Ford,E350,"ac, abs, moon",3000.00\n'''
    '''1999,Chevy,"Venture ""Extended Edition""","",4900.00\n'''
    '''1999,Chevy,"Venture ""Extended Edition, Very Large""",,5000.00\n'''
    '''1996,Jeep,Grand Cherokee,"MUST SELL!\n'''
    '''air, moon roof, loaded",4799.00\n''')

HEADER = 'year,brand,model,detail,other\n'

VALID_WITH_HEADER = HEADER + VALID_CSV

MISSING_END_QUOTE = VALID_CSV + \
    '1999,Chevy,"Venture ""Extended Edition"","",4900.00\n'

@pytest.mark.parametrize(
    ['csv_text', 'result_dict', 'prefix', 'header'],
    [
        (VALID_CSV, {
            'purpose': 'Test valid file.',
            'stdout_part': 'successfully',
            'stderr_part': '',
            'streams': {0: {'stream_type': 'text',
                            'index': 0,
                            'mimetype': MIMETYPE,
                            'version': '',
                            'delimiter': ',',
                            'separator': '\n',
                            'first_line': ['1997', 'Ford', 'E350', 'ac, abs, moon',
                                          '3000.00']}}}, 'valid__', None),
        (VALID_WITH_HEADER, {
            'purpose': 'Test valid file with header.',
            'stdout_part': 'successfully',
            'stderr_part': '',
            'streams': {0: {'stream_type': 'text',
                            'index': 0,
                            'mimetype': MIMETYPE,
                            'version': '',
                            'delimiter': ',',
                            'separator': '\n',
                            'first_line': ['year', 'brand', 'model', 'detail', 'other']
                           }}}, 'valid__', ['year', 'brand', 'model', 'detail', 'other']),
        (MISSING_END_QUOTE, {
            'purpose': 'Test missing end quote',
            'stdout_part': '',
            'stderr_part': 'unexpected end of data',
            'streams': {0: {'stream_type': 'text',
                            'index': 0,
                            'mimetype': MIMETYPE,
                            'version': '',
                            'delimiter': ',',
                            'separator': '\n',
                            'first_line': ['1997', 'Ford', 'E350', 'ac, abs, moon',
                                          '3000.00']}}}, 'invalid__', None),
        (HEADER, {
            'purpose': 'Test single field',
            'stdout_part': 'successfully',
            'stderr_part': '',
            'streams': {0: {'stream_type': 'text',
                            'index': 0,
                            'mimetype': MIMETYPE,
                            'version': '',
                            'delimiter': ';',
                            'separator': '\n',
                            'first_line': ['year,brand,model,detail,other']
                           }}}, 'valid__', ['year,brand,model,detail,other']),
        (VALID_WITH_HEADER, {
            'purpose': 'Invalid delimiter',
            'stdout_part': '',
            'stderr_part': 'CSV validation error: field counts',
            'streams': {0: {'stream_type': 'text',
                            'index': 0,
                            'mimetype': MIMETYPE,
                            'version': '',
                            'delimiter': ';',
                            'separator': '\n',
                            'first_line': ['year,brand,model,detail,other']
                           }}}, 'invalid__',
            ['year', 'brand', 'model', 'detail', 'other'])
    ]
)
def test_scraper(csv_text, result_dict, prefix, header):
    """Write test data and run csv scraping for the file"""

    with NamedTemporaryFile(delete=False, prefix=prefix) as outfile:

        try:
            outfile.write(csv_text)
            outfile.close()

            words = outfile.name.rsplit("/", 1)
            correct = parse_results(words[1], '', result_dict,
                                    True, basepath=words[0])
            correct.mimetype = MIMETYPE
            correct.streams[0]['mimetype'] = MIMETYPE
            scraper = Csv(
                correct.filename, correct.mimetype, True, params={
                    'separator': correct.streams[0]['separator'],
                    'delimiter': correct.streams[0]['delimiter'],
                    'fields': header})
            scraper.scrape_file()
        finally:
            os.unlink(outfile.name)

    assert scraper.mimetype == correct.mimetype
    assert scraper.version == correct.version
    assert scraper.streams == correct.streams
    assert scraper.info['class'] == 'Csv'
    assert correct.stdout_part in scraper.messages()
    assert correct.stderr_part in scraper.errors()
    assert scraper.well_formed == correct.well_formed


def test_pdf_as_csv():
    """Test CSV scraper with PDF files"""

    scraper = Csv(PDF_PATH, MIMETYPE)
    scraper.scrape_file()

    assert not scraper.well_formed, scraper.messages() + scraper.errors()
    assert "successfully" not in scraper.messages()
    assert len(scraper.errors()) > 0


def test_no_parameters():
    """Test scraper without separate parameters"""
    with NamedTemporaryFile(delete=False) as outfile:

        try:
            outfile.write(VALID_CSV)
            outfile.close()

            scraper = Csv(outfile.name, MIMETYPE)
            scraper.scrape_file()
        finally:
            os.unlink(outfile.name)

    assert scraper.mimetype == MIMETYPE
    assert scraper.version == ''
    assert 'successfully' in scraper.messages()
    assert scraper.well_formed == True


def test_is_supported():
    """Test is_supported method"""
    mime = MIMETYPE
    ver = ''
    assert Csv.is_supported(mime, ver, True)
    assert Csv.is_supported(mime, None, True)
    assert Csv.is_supported(mime, ver, False)
    assert Csv.is_supported(mime, 'foo', True)
    assert not Csv.is_supported('foo', ver, True)
