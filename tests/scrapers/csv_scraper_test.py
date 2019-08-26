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
    - MIME type other than 'text/csv' is not supported.
    - Not giving CsvMeta enough parameters causes an error to be raised.
    - Non-existent files are not well-formed and the inability to read the
      file is logged as an error.
"""
from __future__ import unicode_literals

import os
import pytest
import six

from file_scraper.csv.csv_model import CsvMeta
from file_scraper.csv.csv_scraper import CsvScraper
from tests.common import parse_results, partial_message_included

MIMETYPE = "text/csv"

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


# pylint: disable=too-many-arguments
@pytest.mark.parametrize(
    ['csv_text', 'result_dict', 'prefix', 'header', 'extra_params'],
    [
        (VALID_CSV, {
            'purpose': 'Test valid file.',
            'stdout_part': 'successfully',
            'stderr_part': '',
            'streams': {0: {'stream_type': 'text',
                            'index': 0,
                            'mimetype': MIMETYPE,
                            'version': '(:unap)',
                            'delimiter': ',',
                            'separator': '\n',
                            'first_line': ['1997', 'Ford', 'E350',
                                           'ac, abs, moon',
                                           '3000.00']}}},
         'valid__', None, {}),
        (VALID_CSV, {
            'purpose': 'Test forcing the correct MIME type.',
            'stdout_part': 'successfully',
            'stderr_part': '',
            'streams': {0: {'stream_type': 'text',
                            'index': 0,
                            'mimetype': MIMETYPE,
                            'version': '(:unap)',
                            'delimiter': ',',
                            'separator': '\n',
                            'first_line': ['1997', 'Ford', 'E350',
                                           'ac, abs, moon',
                                           '3000.00']}}},
         'valid__', None, {'mimetype': MIMETYPE}),
        (VALID_CSV, {
            'purpose': 'Test forcing other MIME type.',
            'stdout_part': 'successfully',
            'stderr_part': 'MIME type unsupported/mime with version (:unap) '
                           'is not supported',
            'streams': {0: {'stream_type': 'text',
                            'index': 0,
                            'mimetype': 'unsupported/mime',
                            'version': '(:unap)',
                            'delimiter': ',',
                            'separator': '\n',
                            'first_line': ['1997', 'Ford', 'E350',
                                           'ac, abs, moon',
                                           '3000.00']}}},
         'valid__', None, {'mimetype': 'unsupported/mime'}),
        (VALID_CSV, {
            'purpose': 'Test forcing MIME type and version.',
            'stdout_part': 'successfully',
            'stderr_part': 'MIME type unsupported/mime with version 99.9 is '
                           'not supported',
            'streams': {0: {'stream_type': 'text',
                            'index': 0,
                            'mimetype': 'unsupported/mime',
                            'version': '99.9',
                            'delimiter': ',',
                            'separator': '\n',
                            'first_line': ['1997', 'Ford', 'E350',
                                           'ac, abs, moon',
                                           '3000.00']}}},
         'valid__', None, {'mimetype': 'unsupported/mime', 'version': '99.9'}),
        (VALID_WITH_HEADER, {
            'purpose': 'Test valid file with header.',
            'stdout_part': 'successfully',
            'stderr_part': '',
            'streams': {0: {'stream_type': 'text',
                            'index': 0,
                            'mimetype': MIMETYPE,
                            'version': '(:unap)',
                            'delimiter': ',',
                            'separator': '\n',
                            'first_line': ['year', 'brand', 'model', 'detail',
                                           'other']}}},
         'valid__', ['year', 'brand', 'model', 'detail', 'other'], {}),
        (MISSING_END_QUOTE, {
            'purpose': 'Test missing end quote',
            'stdout_part': '',
            'stderr_part': 'unexpected end of data',
            'streams': {0: {'stream_type': 'text',
                            'index': 0,
                            'mimetype': MIMETYPE,
                            'version': '(:unap)',
                            'delimiter': ',',
                            'separator': '\n',
                            'first_line': ['1997', 'Ford', 'E350',
                                           'ac, abs, moon',
                                           '3000.00']}}},
         'invalid__', None, {}),
        (HEADER, {
            'purpose': 'Test single field',
            'stdout_part': 'successfully',
            'stderr_part': '',
            'streams': {0: {'stream_type': 'text',
                            'index': 0,
                            'mimetype': MIMETYPE,
                            'version': '(:unap)',
                            'delimiter': ';',
                            'separator': '\n',
                            'first_line': ['year,brand,model,detail,other']}}},
         'valid__', ['year,brand,model,detail,other'], {}),
        (VALID_WITH_HEADER, {
            'purpose': 'Invalid delimiter',
            'stdout_part': '',
            'stderr_part': 'CSV not well-formed: field counts',
            'streams': {0: {'stream_type': 'text',
                            'index': 0,
                            'mimetype': MIMETYPE,
                            'version': '(:unap)',
                            'delimiter': ';',
                            'separator': '\n',
                            'first_line': ['year,brand,model,detail,other']}}},
         'invalid__', ['year', 'brand', 'model', 'detail', 'other'], {})
    ]
)
def test_scraper(testpath, csv_text, result_dict, prefix, header,
                 evaluate_scraper, extra_params):
    """
    Write test data and run csv scraping for the file.

    NB: Forcing unsupported MIME type causes an error to be logged, resulting
        in the file being reported as not well-formed regardless of its
        contents.
    """

    with open(os.path.join(testpath, '%s.csv' % prefix), 'wb') as outfile:
        outfile.write(csv_text)

    mimetype = result_dict['streams'][0]['mimetype']
    version = result_dict['streams'][0]['version']

    words = outfile.name.rsplit('/', 1)
    correct = parse_results(words[1], '', result_dict,
                            True, basepath=words[0])
    correct.update_mimetype(mimetype)
    correct.update_version(version)
    if mimetype != 'text/csv':
        correct.well_formed = False

    params = {
        'separator': correct.streams[0]['separator'],
        'delimiter': correct.streams[0]['delimiter'],
        'fields': header}
    params.update(extra_params)
    scraper = CsvScraper(correct.filename, True, params=params)
    scraper.scrape_file()

    evaluate_scraper(scraper, correct)
# pylint: enable=too-many-arguments


def test_pdf_as_csv():
    """Test CSV scraper with PDF files."""

    scraper = CsvScraper(PDF_PATH)
    scraper.scrape_file()

    assert not scraper.well_formed, scraper.messages() + scraper.errors()
    assert not partial_message_included('successfully', scraper.messages())
    assert scraper.errors()


def test_no_parameters(testpath, evaluate_scraper):
    """Test scraper without separate parameters."""
    with open(os.path.join(testpath, 'valid__.csv'), 'wb') as outfile:
        outfile.write(VALID_CSV)

    scraper = CsvScraper(outfile.name)
    scraper.scrape_file()

    correct = parse_results('valid__.csv', MIMETYPE,
                            {'purpose': 'Test valid file on default settings.',
                             'stdout_part': 'successfully',
                             'stderr_part': '',
                             'streams':
                             {0: {'stream_type': 'text',
                                  'index': 0,
                                  'mimetype': MIMETYPE,
                                  'version': '',
                                  'delimiter': ',',
                                  'separator': '\r\n',
                                  'first_line': ['1997', 'Ford', 'E350',
                                                 'ac, abs, moon',
                                                 '3000.00']}}},
                            True)
    correct.streams[0]['version'] = "(:unap)"
    evaluate_scraper(scraper, correct)


def test_bad_parameters():
    """
    Test that CsvMeta raises an error if proper parameters are not given.
    """
    with pytest.raises(ValueError) as err:
        # "separator" is missing from the keys
        CsvMeta({"delimiter": ",", "fields": [], "first_line": ""})
    assert ("CsvMeta must be given a dict containing keys" in
            six.text_type(err.value))


def test_nonexistent_file():
    """
    Test that CsvScraper logs an error when file is not found.
    """
    scraper = CsvScraper("nonexistent/file.csv")
    scraper.scrape_file()
    assert partial_message_included("Error when reading the file: ",
                                    scraper.errors())
    assert not scraper.well_formed


def test_no_wellformed(testpath):
    """Test scraper without well-formed check."""
    with open(os.path.join(testpath, 'valid__.csv'), 'wb') as outfile:
        outfile.write(VALID_CSV)

    scraper = CsvScraper(outfile.name, False)
    scraper.scrape_file()

    assert partial_message_included('Skipping scraper', scraper.messages())
    assert scraper.well_formed is None


def test_is_supported():
    """Test is_supported method."""
    mime = MIMETYPE
    ver = ''
    assert CsvScraper.is_supported(mime, ver, True)
    assert CsvScraper.is_supported(mime, None, True)
    assert not CsvScraper.is_supported(mime, ver, False)
    assert CsvScraper.is_supported(mime, 'foo', True)
    assert not CsvScraper.is_supported('foo', ver, True)
