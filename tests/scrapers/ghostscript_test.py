"""
Test for pdf 1.7 ghostscript scraper.
"""

import os

from dpres_scraper.scrapers.ghostscript import GhostScript

BASEPATH = "tests/data/documents"

def test_pdf_1_7_ok():
    """
    test pdf 1.7 ok case
    """
    filename = os.path.join(BASEPATH, "valid_1_7.pdf")
    scraper = GhostScript(filename, 'application/pdf')
    scraper.scrape_file()
    assert 'Error' not in scraper.messages()
    assert scraper.messages() != ""
    assert scraper.well_formed
    assert scraper.errors() == ""


def test_pdf_1_7_validity_error():
    """
    test pdf 1.7 invalid case
    """
    filename = os.path.join(BASEPATH, "invalid_1_7.pdf")
    scraper = GhostScript(filename, 'application/pdf')
    scraper.scrape_file()

    assert 'Unrecoverable error, exit code 1' in scraper.errors()
    assert 'Error: /undefined in obj' in scraper.messages()
    assert not scraper.well_formed


def test_pdf_1_7_version_error():
    """
    test pdf 1.7 wrong version case
    """
    filename = os.path.join(BASEPATH, "invalid_wrong_version.pdf")

    scraper = GhostScript(filename, 'application/pdf')
    scraper.scrape_file()

    assert 'ERROR: wrong file version. Expected PDF 1.7,' \
        ' found PDF document, version 1.3' in scraper.errors()
    assert 'PDF document, version 1.3' in scraper.messages()
    assert not scraper.well_formed


def test_pdfa_valid():
    """Test that valid PDF/A is valid
       This file is also used in veraPDF test, where it should result "valid".
    """
    filename = os.path.join(BASEPATH, "pdfa1-valid.pdf")
    scraper = GhostScript(filename, 'application/pdf')
    scraper.scrape_file()
    assert 'Error' not in scraper.messages()
    assert scraper.messages() != ""
    assert scraper.well_formed
    assert scraper.errors() == ""


def test_pdf_valid_pdfa_invalid():
    """Test that valid PDF (but invalid PDF/A) is valid.
       This file is also used in veraPDF test, where it should result
       "invalid".
    """
    filename = os.path.join(BASEPATH, "pdfa3-fail-a.pdf")
    scraper = GhostScript(filename, 'application/pdf')
    scraper.scrape_file()
    assert 'Error' not in scraper.messages()
    assert scraper.messages() != ""
    assert scraper.well_formed
    assert scraper.errors() == ""


def test_pdf_invalid_pdfa_invalid():
    """Test that invalid PDF (and invalid PDF/A) is invalid.
       This file is also used in veraPDF test, where it should result
       "invalid".
    """
    filename = os.path.join(BASEPATH, "pdfa1-invalid.pdf")
    scraper = GhostScript(filename, 'application/pdf')
    scraper.scrape_file()
    assert not scraper.well_formed
    assert "An error occurred while reading an XREF table." in \
        scraper.errors()
