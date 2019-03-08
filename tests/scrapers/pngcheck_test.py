"""Test the dpres_scraper.scrapers.pngcheck module"""

import os
import dpres_scraper.scrapers.pngcheck


def test_pngcheck_valid():
    """Test valid PNG file"""

    filepath = 'tests/data/image_png/valid_1.2.png'
    scraper = dpres_scraper.scrapers.pngcheck.Pngcheck(filepath, 'image/png')
    scraper.scrape_file()
    assert scraper.well_formed
    assert 'OK' in scraper.messages()
    assert scraper.errors() == ""


def test_pngcheck_invalid():
    """Test corrupted PNG file"""

    filepath = 'tests/data/image_png/invalid_1.2.png'
    scraper = dpres_scraper.scrapers.pngcheck.Pngcheck(filepath, 'image/png')
    scraper.scrape_file()
    assert not scraper.well_formed
    assert 'OK' not in scraper.messages()
    assert 'ERROR' in scraper.errors()
