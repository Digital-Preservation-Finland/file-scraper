"""Test the file_scraper.scrapers.pngcheck module"""
import pytest
from tests.common import parse_results
from file_scraper.scrapers.pngcheck import Pngcheck


MIMETYPE = 'image/png'


@pytest.mark.parametrize(
    ['filename', 'result_dict'],
    [
        ('valid_1.2.png', {
            'purpose': 'Test valid file.'}),
        ('invalid_1.2_no_IEND.png', {
            'purpose': 'Test without IEND.'}),
        ('invalid_1.2_no_IHDR.png', {
            'purpose': 'Test without IHDR.'}),
        ('invalid_1.2_wrong_CRC.png', {
            'purpose': 'Test wrong CRC.'}),
        ('invalid_1.2_wrong_header.png', {
            'purpose': 'Test invalid header.'}),
        ('invalid__empty.png', {
            'purpose': 'Test empty file.'})
    ]
)
def test_scraper(filename, result_dict):
    """Test scraper"""
    correct = parse_results(filename, MIMETYPE,
                            result_dict, True)
    scraper = Pngcheck(correct.filename, correct.mimetype,
                       True, correct.params)
    scraper.scrape_file()
    correct.streams[0]['version'] = None

    assert scraper.mimetype == correct.mimetype
    assert scraper.version is None
    assert scraper.streams == correct.streams
    assert scraper.info['class'] == 'Pngcheck'
    if correct.well_formed:
        assert 'OK' in scraper.messages()
    else:
        assert 'ERROR' in scraper.errors()
    assert scraper.well_formed == correct.well_formed


def test_is_supported():
    """Test is_Supported method"""
    mime = MIMETYPE
    ver = '1.2'
    assert Pngcheck.is_supported(mime, ver, True)
    assert Pngcheck.is_supported(mime, None, True)
    assert not Pngcheck.is_supported(mime, ver, False)
    assert Pngcheck.is_supported(mime, 'foo', True)
    assert not Pngcheck.is_supported('foo', ver, True)
