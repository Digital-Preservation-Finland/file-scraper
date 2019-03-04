"""
Tests for VeraPDF scraper for PDF/A files.
"""

import os
import pytest
from dpres_scraper.scrapers.verapdf import VeraPdf


BASEPATH = "tests/data/documents"


@pytest.mark.parametrize(
    ['filename', 'well_formed', 'errors', 'version'],
    [
        ["pdfa1-valid.pdf", True, "", 'A-1b'],
        ["pdfa2-valid-a.pdf", True, "", 'A-2b'],
        ["pdfa3-valid-a.pdf", True, "", 'A-3b'],
        ["pdfa1-invalid.pdf", False,
         "Couldn't parse stream caused by exception", 'A-1b'],
        ["pdfa2-fail-a.pdf", False,
         "not compliant with Validation Profile requirements", 'A-2b'],
        ["pdfa3-fail-a.pdf", False,
         "not compliant with Validation Profile requirements", 'A-3b'],
        ["../images/valid.tif", False,
         "SEVERE", 'A-3b'],
    ]
)
def test_scrape_file(filename, well_formed, errors, version):
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
