
"""
Tests for DPX scraper.
"""

import os
import pytest
from dpres_scraper.scrapers.dpx import Dpx


BASEPATH = "tests/data/images/"


@pytest.mark.parametrize(
    'filename',
    [
        "valid_2.0.dpx"
    ]
)
def test_scrape_valid_file(filename):

    scraper = Dpx(os.path.join(BASEPATH, filename), 'image/x-dpx')
    scraper.scrape_file()
    assert scraper.well_formed


@pytest.mark.parametrize(
    'filename',
    [
        "invalid_2.0_file_size_error.dpx", "invalid_2.0_empty_file.dpx",
    ]
)
def test_scrape_invalid_file(filename):

    scraper = Dpx(filename, 'image/x-dpx')
    scraper.scrape_file()
    assert not scraper.well_formed
