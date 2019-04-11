"""
Schematron scraper tests

This module tests that:
    - MIME type, version, streams and well-formedness are scraped correctly.
    - For well-formed files, scraper messages contains
      '<svrl:schematron-output'.
    - For empty files, scraper errors contains 'Document is empty'.
    - If and only if verbose option is set to False, scraper messages also
      contain 'have been suppressed'.
    - If well-formedness is not tested, scraper messages contain 'Skipping
      scraper' and well_formed is None

    - is_supported(cls, mimetype, version, check_wellformed, params) returns
      False if params does not contain 'schematron' as a key.
    - is_supported also returns False if check_wellformed is False.
    - MIME type 'text/xml' with version 1.0 or made-up version is supported.
    - A made up MIME type is not supported.

    - If schematron is not given any parameters, instance variables are given
      the following values:
        - _schematron_file is None
        - _extra_hash is None
        - _verbose is False
        - _cache is True
    - If the variables above are given new values as parameters, these values
      affect the instance variables.

    - XSLT filenames are generated using sha1 algorithm on
      [_schematron_file][verbosity][ _extra_hash]
      where [verbosity] is "verbose" if verbose is True, otherwise "".

    - Schematron removes extra copies of identical elements, but not if their
      attributes differ.
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
             ROOTPATH, 'tests/data/text_xml/local.sch'),
             'cache': False}),
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
def test_scraper(filename, result_dict, params, evaluate_scraper):
    """Test scraper."""

    correct = parse_results(filename, 'text/xml',
                            result_dict, True, params)
    scraper = Schematron(correct.filename, correct.mimetype,
                         True, correct.params)
    scraper.scrape_file()
    correct.version = None
    correct.streams[0]['version'] = None

    evaluate_scraper(scraper, correct)

    if 'verbose' in correct.params and correct.params['verbose']:
        assert 'have been suppressed' not in scraper.messages()
    elif scraper.messages():
        assert 'have been suppressed' in scraper.messages()


def test_no_wellformed():
    """Test scraper without well-formed check."""
    scraper = Schematron('tests/data/text_xml/valid_1.0_wellformed.xml',
                         'text/xml', False)
    scraper.scrape_file()
    assert 'Skipping scraper' in scraper.messages()
    assert scraper.well_formed is None


def test_is_supported():
    """Test is_supported method."""
    mime = 'text/xml'
    ver = '1.0'
    assert Schematron.is_supported(mime, ver, True, {'schematron': None})
    assert not Schematron.is_supported(mime, ver, True)
    assert Schematron.is_supported(mime, None, True, {'schematron': None})
    assert not Schematron.is_supported(mime, ver, False, {'schematron': None})
    assert Schematron.is_supported(mime, 'foo', True, {'schematron': None})
    assert not Schematron.is_supported('foo', ver, True, {'schematron': None})


def test_parameters():
    """Test that parameters and default values work properly."""
    # pylint: disable=protected-access
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
    assert scraper._extra_hash == 'abc'
    assert scraper._verbose
    assert not scraper._cache


def test_xslt_filename():
    """Test that checksum for xslt filename is calculated properly."""
    # pylint: disable=protected-access
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
    """Test duplicate element filtering."""
    # pylint: disable=protected-access
    schtest = \
        b"""<svrl:schematron-output
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
    assert result.count(b'<svrl:active-pattern') == 1
    assert result.count(b'<svrl:fired-rule') == 1
    assert result.count(b'<svrl:failed-assert') == 2
