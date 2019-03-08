"""
Tests for Vnu scraper.
"""

import os
import pytest
from dpres_scraper.scrapers.vnu import Vnu


BASEPATH = "tests/data/text_html"


@pytest.mark.parametrize(
    ['filename', 'well_formed', 'errors'
    ],
    [["valid_5.0.html", True, ""],
     ["invalid_5.0_wrong_encoding.html", False,
      "Internal encoding declaration"]
    ]
)
def test_scrape_valid_file(filename, well_formed, errors):
    """
    Test scraping of HTML5 files.
    """
    scraper = Vnu(os.path.join(BASEPATH, filename), 'text/html')
    scraper.scrape_file()

    # Is validity expected?
    assert scraper.well_formed is well_formed

    # Is stderr output expected?
    if errors == "":
        assert scraper.errors() == ""
    else:
        assert errors in scraper.errors()

    # Is stdout output expected?
    assert scraper.filename + "\n" == scraper.messages()
