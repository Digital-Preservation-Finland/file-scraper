"""Test module for jhove.py"""
import os
import pytest

from dpres_scraper.scrapers.jhove import GifJHove, TiffJHove, PdfJHove, \
    Utf8JHove, JpegJHove, HtmlJHove, WavJHove

TESTDATADIR_BASE = 'tests/data'


@pytest.mark.parametrize(
    ["scraper_class", "filename", "mimetype"],
    [
        (HtmlJHove, "text/valid_4.html", "text/html"),
        (GifJHove, "images/valid_89a.gif", "image/gif"),
        (GifJHove, "images/valid_87a.gif", "image/gif"),
        (TiffJHove, "images/valid.tif", "image/tiff"),
        (PdfJHove, "documentss/valid_1_4.pdf", "application/pdf"),
        (PdfJHove, "documents/valid_1_5.pdf", "application/pdf"),
        (PdfJHove, "documents/valid_1_6.pdf", "application/pdf"),
        (PdfJHove, "documents/pdfa2-valid-a.pdf", "application/pdf"),
        (PdfJHove, "documents/pdfa3-valid-a.pdf", "application/pdf"),
        (PdfJHove, "documents/pdfa1-valid.pdf", "application/pdf"),
        (PdfJHove, "documents/pdfa2-fail-a.pdf", "application/pdf"),
        (PdfJHove, "documents/pdfa3-fail-a.pdf", "application/pdf"),
        (TiffJHove, "images/valid_5.tif", "image/tiff"),
        (HtmlJHove, "text/valid.xhtml", "application/xhtml+xml"),
        (WavJHove, "audio/valid-wav.wav", "audio/x-wav"),
        (WavJHove, "audio/valid-bwf.wav", "audio/x-wav")
    ])
def test_scrape_valid_form_and_version(
        scraper_class, filename, mimetype):
    """Test cases of Jhove scraping"""
    file_path = os.path.join(TESTDATADIR_BASE, filename)
    scraper = scraper_class(file_path, mimetype)
    scraper.scrape_file()
    assert scraper.well_formed, scraper.errors()
    assert "Well-Formed and valid" in scraper.messages()
    assert scraper.errors() == ""


@pytest.mark.parametrize(
    ["scraper_class", "filename", "mimetype"],
    [
        (JpegJHove, "images/valid.jpg", "image/jpeg"),
        (Utf8JHove, "text/utf8.txt", "text/plain"),
        (Utf8JHove, "text/utf8.csv", "text/plain"),
        (Utf8JHove, "html/valid_4.html", "text/html")
    ])
def test_scrape_valid_only_form(scraper_class, filename, mimetype):
    """Test cases of Jhove scraping"""
    file_path = os.path.join(TESTDATADIR_BASE, filename)
    scraper = scraper_class(file_path, mimetype)
    scraper.scrape_file()
    assert scraper.well_formed, scraper.errors()
    assert "Well-Formed and valid" in scraper.messages()
    assert "OK" in scraper.messages()
    assert scraper.errors() == ""


@pytest.mark.parametrize(
    ["scraper_class", "filename", "mimetype", "stdout"],
    [
        (HtmlJHove, "text/invalid_4.htm",
         "text/html", "Well-Formed, but not valid"),
        (GifJHove, "invalid.gif",
         "image/gif", "Not well-formed"),
        (GifJHove, "images/invalid_89a.gif",
         "image/gif", "Not well-formed"),
        (PdfJHove, "documents/pdfa1-fail.pdf",
         "application/pdf", "Not well-formed"),
        (TiffJHove, "images/invalid.tif",
         "image/tiff", "Not well-formed"),
        (Utf8JHove, "text/iso-8859.txt",
         "text/plain", "Not well-formed"),
        (WavJHove,
         "audio/invalid-wav-last-byte-missing.wav",
         "audio/x-wav", "Not well-formed"),
    ])
def test_scrape_invalid(scraper_class, filename, mimetype, stdout):
    """Test cases of Jhove scraping"""
    file_path = os.path.join(TESTDATADIR_BASE, filename)
    scraper = scraper_class(file_path, mimetype)
    scraper.scrape_file()
    assert not scraper.well_formed, scraper.messages() + scraper.errors()
    assert stdout in scraper.messages()
    assert scraper.errors() != ""
