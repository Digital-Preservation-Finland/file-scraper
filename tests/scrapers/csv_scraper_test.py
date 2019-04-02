"""
Tests for Csv scraper

This module tests that:
    - mimetype, version and streams are scraped correctly when a csv file is
      scraped.
    - scraper class used for csv scraping is Csv.
    - well-formedness of csv files is determined accurately.
    - scraper reports errors in scraping as expected when there is a missing
      quote or wrong field delimiter is given.
    - scraping a file other than csv file results in:
        - not well-formed
        - success not reported in scraper messages
        - some error recorded by the scraper
    - scraper is able to extract the MIME type of a well-formed file and
      guess the file as a well-formed one also when separator, delimiter
      and fields are not given by user.
    - well-formed result is None when skipping wellformed check.
    - all files with MIME type 'text/csv' are reported to be supported with
      full well-formed check and for empty, None or arbitrary string as the
      version.
    - MIME type other than 'text/csv' is not supported
"""

import os
import pytest

from file_scraper.scrapers.csv_scraper import Csv
from tests.common import parse_results

MIMETYPE = 'text/csv'

PDF_PATH = os.path.join(
    'tests/data/application_pdf/valid_1.4.pdf')

VALID_CSV = (
    b'''1997,Ford,E350,"ac, abs, moon",3000.00\n'''
    b'''1999,Chevy,"Venture ""Extended Edition""","",4900.00\n'''
    b'''1999,Chevy,"Venture ""Extended Edition, Very Large""",,5000.00\n'''
    b'''1996,Jeep,Grand Cherokee,"MUST SELL!\n'''
    b'''air, moon roof, loaded",4799.00\n''')

HEADER = b'year,brand,model,detail,other\n'

VALID_WITH_HEADER = HEADER + VALID_CSV

MISSING_END_QUOTE = VALID_CSV + \
                    b'1999,Chevy,"Venture ""Extended Edition"","",4900.00\n'


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
                            'first_line': ['1997', 'Ford', 'E350',
                                           'ac, abs, moon',
                                           '3000.00']}}},
         'valid__', None),
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
                            'first_line': ['year', 'brand', 'model', 'detail',
                                           'other']}}},
         'valid__', ['year', 'brand', 'model', 'detail', 'other']),
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
                            'first_line': ['1997', 'Ford', 'E350',
                                           'ac, abs, moon',
                                           '3000.00']}}},
         'invalid__', None),
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
                            'first_line': ['year,brand,model,detail,other']}}},
         'valid__', ['year,brand,model,detail,other']),
        (VALID_WITH_HEADER, {
            'purpose': 'Invalid delimiter',
            'stdout_part': '',
            'stderr_part': 'CSV not well-formed: field counts',
            'streams': {0: {'stream_type': 'text',
                            'index': 0,
                            'mimetype': MIMETYPE,
                            'version': '',
                            'delimiter': ';',
                            'separator': '\n',
                            'first_line': ['year,brand,model,detail,other']}}},
         'invalid__', ['year', 'brand', 'model', 'detail', 'other'])
    ]
)
def test_scraper(testpath, csv_text, result_dict, prefix, header,
                 evaluate_scraper):
    """Write test data and run csv scraping for the file."""

    with open(os.path.join(testpath, '%s.csv' % prefix), 'wb') as outfile:
        outfile.write(csv_text)

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

    evaluate_scraper(scraper, correct)


def test_pdf_as_csv():
    """Test CSV scraper with PDF files."""

    scraper = Csv(PDF_PATH, MIMETYPE)
    scraper.scrape_file()

    assert not scraper.well_formed, scraper.messages() + scraper.errors()
    assert "successfully" not in scraper.messages()
    assert scraper.errors()


def test_no_parameters(testpath):
    """Test scraper without separate parameters."""
    with open(os.path.join(testpath, 'valid__.csv'), 'wb') as outfile:
        outfile.write(VALID_CSV)

    scraper = Csv(outfile.name, MIMETYPE)
    scraper.scrape_file()

    assert scraper.mimetype == MIMETYPE
    assert scraper.version == ''
    assert 'successfully' in scraper.messages()
    assert scraper.well_formed


def test_no_wellformed(testpath):
    """Test scraper without well-formed check."""
    with open(os.path.join(testpath, 'valid__.csv'), 'wb') as outfile:
        outfile.write(VALID_CSV)

    scraper = Csv(outfile, 'text/csv', False)
    scraper.scrape_file()

    assert 'Skipping scraper' in scraper.messages()
    assert scraper.well_formed is None


def test_is_supported():
    """Test is_supported method."""
    mime = MIMETYPE
    ver = ''
    assert Csv.is_supported(mime, ver, True)
    assert Csv.is_supported(mime, None, True)
    assert not Csv.is_supported(mime, ver, False)
    assert Csv.is_supported(mime, 'foo', True)
    assert not Csv.is_supported('foo', ver, True)
