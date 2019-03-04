"""Test the dpres_scraper.scrapers.pngcheck module"""

import os
import dpres_scraper.scrapers.pngcheck


def test_pngcheck_valid():
    """Test scraperid PNG file"""

    filepath = 'tests/data/images/scraperid.png'
    scraper = dpres_scraper.scrapers.pngcheck.Pngcheck(filepath, 'image/png')
    scraper.scrape_file()
    assert scraper.well_formed
    assert 'OK' in scraper.messages()
    assert scraper.errors() == ""


def test_pngcheck_invalid():
    """Test corrupted PNG file"""

    filepath = 'tests/data/images/inscraperid.png'
    scraper = dpres_scraper.scrapers.pngcheck.Pngcheck(filepath, 'image/png')
    scraper.scrape_file()
    assert not scraper.well_formed
    assert 'OK' not in scraper.messages()
    assert 'ERROR' in scraper.errors()
