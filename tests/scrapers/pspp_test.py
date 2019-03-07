"""
Tests for PSPP scraper.
"""

import os
import pytest
from dpres_scraper.scrapers.pspp import Pspp


BASEPATH = "tests/data/spss"


@pytest.mark.parametrize(
    ['filename', 'mimetype', 'validity'],
    [
        ("valid.por", "application/x-spss-por", True),
        ("empty.por", "application/x-spss-por", False),
        ("example.sps", "application/x-spss-por", False),
        ("invalid_wrong_spss_format.sav", "application/x-spss-por", False),
        ("ISSP2000_sample_corrupted.por", "application/x-spss-por", False)
    ]
)
def test_scrape_valid_file(filename, mimetype, validity):

    scraper = Pspp(os.path.join(BASEPATH, filename), mimetype)
    scraper.scrape_file()
    assert scraper.well_formed == validity
