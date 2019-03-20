"""Schematron scraper tests
"""
import os
import pytest
from file_scraper.scrapers.schematron import Schematron
from tests.common import parse_results

ROOTPATH = os.path.abspath(os.path.join(
    os.path.dirname(__file__), '../../'))

@pytest.mark.parametrize(
    ['filename', 'result_dict', 'params'],
    [
        ('valid_1.0_well_formed.xml', {
            'purpose': 'Test valid file',
            'stdout_part': '<svrl:schematron-output',
            'stderr_part': ''},
         {'schematron': os.path.join(
            ROOTPATH, 'tests/data/text_xml/local.sch')}),
        ('invalid_1.0_local_xsd.xml', {
            'purpose': 'Test invalid file',
            'stdout_part': '<svrl:schematron-output',
            'stderr_part': ''},
         {'schematron': 'tests/data/text_xml/local.sch',
          'verbose': True, 'cache': False}),
        ('invalid__empty.xml', {
            'purpose': 'Test invalid xml with given schema.',
            'stdout_part': '',
            'stderr_part': 'Document is empty'},
         {'schematron': 'tests/data/text_xml/local.sch'}),
    ]
)
def test_scraper_invalid(filename, result_dict, params):
    """Test scraper"""

    correct = parse_results(filename, 'text/xml',
                            result_dict, True, params)
    scraper = Schematron(correct.filename, correct.mimetype,
                         True, correct.params)
    scraper.scrape_file()
    correct.version = None
    correct.streams[0]['version'] = None

    assert scraper.mimetype == correct.mimetype
    assert scraper.version == correct.version
    assert scraper.streams == correct.streams
    assert scraper.info['class'] == 'Schematron'
    assert correct.stdout_part in scraper.messages()
    assert correct.stderr_part in scraper.errors()
    assert scraper.well_formed == correct.well_formed

    if 'verbose' in correct.params and correct.params['verbose']:
        assert not 'have been suppressed' in scraper.messages()
    elif len(scraper.messages()) > 0:
        assert 'have been suppressed' in scraper.messages()


def test_is_supported():
    """Test is_Supported method"""
    mime = 'text/xml'
    ver = '1.0'
    assert Schematron.is_supported(mime, ver, True, {'schematron': None})
    assert not Schematron.is_supported(mime, ver, True)
    assert Schematron.is_supported(mime, None, True, {'schematron': None})
    assert not Schematron.is_supported(mime, ver, False, {'schematron': None})
    assert not Schematron.is_supported(mime, 'foo', True, {'schematron': None})
    assert not Schematron.is_supported('foo', ver, True, {'schematron': None})


def test_parameters():
    """Test that parameters and default values work properly.
    """
    scraper = Schematron('testsfile', 'test/mimetype')
    assert scraper._schematron_file is None
    assert scraper._extra_hash is None
    assert not scraper._verbose
    assert scraper._cache

    scraper = Schematron('testfile', 'text/xml',
                         params={'schematron': 'schfile',
                                 'extra_hash': 'abc',
                                 'verbose': True,
                                 'cache': False})
    assert scraper._schematron_file == 'schfile'
    assert scraper._extra_hash is 'abc'
    assert scraper._verbose
    assert not scraper._cache


def test_xslt_filename():
    """Test that schecksum for xslt filename is calculated properly.
    """
    scraper = Schematron('filename', 'text/xml')
    scraper._schematron_file = 'tests/data/text_xml/local.sch'
    assert '76ed62' in scraper._generate_xslt_filename()
    scraper._verbose = True
    assert 'ddb11a' in scraper._generate_xslt_filename()
    scraper._extra_hash = 'abc'
    assert '550d66' in scraper._generate_xslt_filename()
    scraper._verbose = False
    assert '791b2e' in scraper._generate_xslt_filename()

def test_filter_duplicate_elements():
    """Test duplicate element filtering.
    """
    schtest = \
        """<svrl:schematron-output
            xmlns:svrl="http://purl.oclc.org/dsdl/svrl">
               <svrl:active-pattern id="id"/>
               <svrl:active-pattern id="id"/>
               <svrl:fired-rule context="context"/>
               <svrl:fired-rule context="context"/>
               <svrl:failed-assert test="test">
                   <svrl:text>string</svrl:text>
               </svrl:failed-assert>
               <svrl:failed-assert test="test 2">
                   <svrl:text>string</svrl:text>
               </svrl:failed-assert>
               <svrl:fired-rule context="context"/>
               <svrl:active-pattern id="id"/>
           </svrl:schematron-output>"""
    scraper = Schematron('filename', 'text/xml')
    result = scraper._filter_duplicate_elements(schtest)
    assert result.count('<svrl:active-pattern') == 1
    assert result.count('<svrl:fired-rule') == 1
    assert result.count('<svrl:failed-assert') == 2
