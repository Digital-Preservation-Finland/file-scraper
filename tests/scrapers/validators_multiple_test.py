"""
Tests office-file scraping with combination of Office-scraper and
File-scraper.
"""

import os
import pytest
from file_scraper.iterator import iter_scrapers
from pprint import pprint


BASEPATH = "tests/data"


# Test valid file
@pytest.mark.parametrize(
    ['filename', 'mimetype'],
    [
        ("valid_1.1.odt", "application/vnd.oasis.opendocument.text"),
    ]
)
def test_scrape_valid_file(filename, mimetype):
    for class_ in iter_scrapers(mimetype, None):
        scraper = class_(
            os.path.join(BASEPATH, mimetype.replace('/', '_'), filename),
            mimetype)
        scraper.scrape_file()
        assert scraper.well_formed

# Test invalid files
@pytest.mark.parametrize(
    ['filename', 'mimetype'],
    [
        # Corrupted file - caught by Office scraper
        ("ODF_Text_Document_corrupted.odt",
         "application/vnd.oasis.opendocument.text"),
        # Wrong MIME - caught by File scraper
        ("valid_1.1.odt", "application/msword"),
    ]
)
def test_scrape_invalid_file(filename, mimetype):
    scraper_results = []
    for class_ in iter_scrapers(mimetype, None):
        scraper = class_(
            os.path.join(BASEPATH, "application_vnd.oasis.opendocument.text", filename),
            mimetype)
        scraper_results.append(scraper.well_formed)

    assert not all(scraper_results)
    assert len(scraper_results) > 0
