"""Schematron scraper tests
"""
import os
import pytest
from file_scraper.scrapers.schematron import Schematron
from tests.scrapers.common import parse_results

ROOTPATH = os.path.abspath(os.path.join(
    os.path.dirname(__file__), '../../'))

# TODO: Remove dependency to dpres-xml-schemas

@pytest.mark.parametrize(
    ['filename', 'result_dict', 'params'],
    [
        ('valid_1.0_well_formed.xml', {
            'purpose': 'Test valid file',
            'stdout_part': '<svrl:schematron-output',
            'stderr_part': ''},
         {'schematron': os.path.join(ROOTPATH, 'tests/data/text_xml/local.sch'),
          'compile_path': '/usr/share/iso_schematron_xslt1'}),
        ('invalid_1.0_local_xsd.xml', {
            'purpose': 'Test invalid file',
            'stdout_part': '<svrl:schematron-output',
            'stderr_part': ''},
         {'schematron': 'tests/data/text_xml/local.sch',
          'compile_path': '/usr/share/iso_schematron_xslt1',
          'verbose': True, 'cache': False}),
        ('invalid__empty.xml', {
            'purpose': 'Test invalid xml with given schema.',
            'stdout_part': '',
            'stderr_part': 'Document is empty'},
         {'schematron': 'tests/data/text_xml/local.sch',
          'compile_path': '/usr/share/iso_schematron_xslt1'}),
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
