"""Xmllint scraper tests
"""
import os
import pytest
from file_scraper.scrapers.xmllint import Xmllint
from tests.scrapers.common import parse_results

ROOTPATH = os.path.abspath(os.path.join(
    os.path.dirname(__file__), '../../'))


@pytest.mark.parametrize(
    ['filename', 'result_dict', 'params'],
    [
        ('valid_1.0_well_formed.xml', {
            'purpose': 'Test valid file without schema.',
            'stdout_part': 'Document is well-formed but does not contain schema.',
            'stderr_part': ''},
         {'catalogs': False}),
        ('valid_1.0_local_xsd.xml', {
            'purpose': 'Test valid xml with given schema.',
            'stdout_part': 'Success',
            'stderr_part': ''},
         {'catalogs': False, 'schema': os.path.join(ROOTPATH, 'tests/data/text_xml/local.xsd')}),
        ('valid_1.0_dtd.xml', {
            'purpose': 'Test valid xml with dtd.',
            'stdout_part': 'Success',
            'stderr_part': ''},
         {'catalogs': False})
    ]
)
def test_scraper_valid(filename, result_dict, params):
    """Test scraper"""

    correct = parse_results(filename, 'text/xml',
                            result_dict, True, params)
    scraper = Xmllint(correct.filename, correct.mimetype,
                      True, correct.params)
    scraper.scrape_file()

    assert scraper.mimetype == correct.mimetype
    assert scraper.version == correct.version
    assert scraper.streams == correct.streams
    assert scraper.info['class'] == 'Xmllint'
    assert correct.stdout_part in scraper.messages()
    assert not '<note>' in scraper.messages()
    assert correct.stderr_part in scraper.errors()
    assert scraper.well_formed == correct.well_formed


@pytest.mark.parametrize(
    ['filename', 'result_dict', 'params'],
    [
        ('invalid_1.0_no_closing_tag.xml', {
            'purpose': 'Test invalid file without schema.',
            'stdout_part': '',
            'stderr_part': 'Opening and ending tag mismatch'},
         {'catalogs': False}),
        ('invalid_1.0_local_xsd.xml', {
            'purpose': 'Test invalid xml with given schema.',
            'stdout_part': '',
            'stderr_part': 'Schemas validity error'},
         {'catalogs': False, 'schema': os.path.join(ROOTPATH, 'tests/data/text_xml/local.xsd')}),
        ('valid_1.0_local_xsd.xml', {
            'purpose': 'Test valid xml with given invalid schema.',
            'inverse': True,
            'stdout_part': '',
            'stderr_part': 'parser error'},
         {'catalogs': False, 'schema': os.path.join(ROOTPATH, 'tests/data/text_xml/invalid_local.xsd')}),
        ('invalid_1.0_dtd.xml', {
            'purpose': 'Test invalid xml with dtd.',
            'stdout_part': '',
            'stderr_part': 'does not follow the DTD'},
         {'catalogs': False}),
        ('invalid__empty.xml', {
            'purpose': 'Test empty xml.',
            'stdout_part': '',
            'stderr_part': 'Document is empty'}, None)
    ]
)
def test_scraper_invalid(filename, result_dict, params):
    """Test scraper"""

    correct = parse_results(filename, 'text/xml',
                            result_dict, True, params)
    scraper = Xmllint(correct.filename, correct.mimetype,
                      True, correct.params)
    scraper.scrape_file()
    if 'empty' in filename or 'no_closing_tag' in filename:
        correct.version = None
        correct.streams[0]['version'] = None

    assert scraper.mimetype == correct.mimetype
    assert scraper.version == correct.version
    assert scraper.streams == correct.streams
    assert scraper.info['class'] == 'Xmllint'
    assert correct.stdout_part in scraper.messages()
    assert not '<note>' in scraper.messages()
    assert correct.stderr_part in scraper.errors()
    assert scraper.well_formed == correct.well_formed


def test_is_supported():
    """Test is_Supported method"""
    mime = 'text/xml'
    ver = '1.0'
    assert Xmllint.is_supported(mime, ver, True)
    assert Xmllint.is_supported(mime, None, True)
    assert not Xmllint.is_supported(mime, ver, False)
    assert not Xmllint.is_supported(mime, 'foo', True)
    assert not Xmllint.is_supported('foo', ver, True)
