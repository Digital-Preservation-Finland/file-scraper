"""
Tests for VeraPDF scraper for PDF/A files.
"""

import os
import pytest
from dpres_scraper.scrapers.verapdf import VeraPdf


BASEPATH = "tests/data/documents"


@pytest.mark.parametrize(
    ['filename', 'well_formed', 'errors'],
    [
        ("valid_A-1b.pdf", True, ""),
        ("valid_A-2b.pdf", True, ""),
        ("valid_A-3b.pdf", True, ""),
        ("invalid_A-1b_corrupted.pdf", False,
         "Couldn't parse stream caused by exception"),
        ("invalid_A-2b.pdf", False,
         "not compliant with Validation Profile requirements"),
        ("invalid_A-3b.pdf", False,
         "not compliant with Validation Profile requirements"),
        ("../images/valid_6.0.tif", False, "SEVERE"),
    ]
)
def test_scrape_file(filename, well_formed, errors):
    """
    Test scraping of PDF/A files. Asserts that valid files are
    valid and invalid files or files with wrong versions are
    not valid. Also asserts that files which aren't PDF files
    are processed correctly.
    """

    scraper = VeraPdf(os.path.join(BASEPATH, filename), 'application/pdf')
    scraper.scrape_file()

    # Is validity expected?
    assert scraper.well_formed == well_formed

    # Is stderr output expected?
    if errors == "":
        assert scraper.errors() == ""
    else:
        assert errors in scraper.errors()
