"""
Tests office-file scraping with combination of Office-scraper and
File-scraper.
"""

import os
import pytest
from dpres_scraper.iterator import iter_scrapers


BASEPATH = "tests/data/documents"


# Test valid file
@pytest.mark.parametrize(
    ['filename', 'mimetype'],
    [
        ("ODF_Text_Document.odt", "application/vnd.oasis.opendocument.text"),
    ]
)
def test_scrape_valid_file(filename, mimetype):
    for scraper in iter_scrapers(
            os.path.join(BASEPATH, filename), mimetype, None):
        assert scraper.well_formed


# Test invalid files
@pytest.mark.parametrize(
    ['filename', 'mimetype'],
    [
        # Corrupted file - caught by Office scraper
        ("ODF_Text_Document_corrupted.odt",
         "application/vnd.oasis.opendocument.text"),
        # Wrong MIME - caught by File scraper
        ("ODF_Text_Document.odt", "application/msword"),
        # Unsupported version number - scraper not found
        ("MS_Word_97-2003.doc", "application/msword"),
    ]
)
def test_scrape_invalid_file(filename, mimetype):
    scraper_results = []
    for scraper in iter_scrapers(
             os.path.join(BASEPATH, filename), mimetype, None):
        scraper_results.append(scraper.well_formed)

    assert not all(scraper_results)
    assert len(scraper_results) > 0
