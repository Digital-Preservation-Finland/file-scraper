
"""
Tests for DPX scraper.
"""

import os
import pytest
from dpres_scraper.scrapers.dpx import Dpx


BASEPATH = "tests/data/video/"


@pytest.mark.parametrize(
    ['filename'],
    [
        ("valid_dpx.dpx", "image/x-dpx")
    ]
)
def test_scrape_valid_file(filename, mimetype):

    scraper = Dpx(filename, 'image/x-dpx')
    scraper.scrape_file()
    assert scraper.well_formed


@pytest.mark.parametrize(
    ['filename'],
    [
        ("corrupted_dpx.dpx"), ("empty_file.dpx"),
    ]
)
def test_scrape_invalid_file(filename):

    scraper = Dpx(filename, 'image/x-dpx')
    scraper.scrape_file()
    assert not scraper.well_formed
