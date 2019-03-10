"""Test module for jhove.py"""
import os
import pytest

from dpres_scraper.scrapers.jhove import GifJHove, TiffJHove, PdfJHove, \
    Utf8JHove, JpegJHove, HtmlJHove, WavJHove

TESTDATADIR_BASE = 'tests/data'


@pytest.mark.parametrize(
    ["scraper_class", "filename", "mimetype"],
    [
        (HtmlJHove, "text_html/valid_4.01.html", "text/html"),
        (GifJHove, "image_gif/valid_1989a.gif", "image/gif"),
        (GifJHove, "image_gif/valid_1987a.gif", "image/gif"),
        (TiffJHove, "image_tiff/valid_6.0.tif", "image/tiff"),
        (PdfJHove, "application_pdf/valid_1.4.pdf", "application/pdf"),
        (PdfJHove, "application_pdf/valid_1.5.pdf", "application/pdf"),
        (PdfJHove, "application_pdf/valid_1.6.pdf", "application/pdf"),
        (PdfJHove, "application_pdf/valid_A-2b.pdf", "application/pdf"),
        (PdfJHove, "application_pdf/valid_A-3b.pdf", "application/pdf"),
        (PdfJHove, "application_pdf/valid_A-1a.pdf", "application/pdf"),
        (HtmlJHove, "application_xhtml+xml/valid_1.0.xhtml",
            "application/xhtml+xml"),
        (WavJHove, "audio_x-wav/valid_wav.wav", "audio/x-wav"),
        (WavJHove, "audio_x-wav/valid_2_bwf.wav", "audio/x-wav")
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
        (JpegJHove, "image_jpeg/valid_1.01.jpg", "image/jpeg"),
        (Utf8JHove, "text_plain/valid_utf8.txt", "text/plain"),
    ])
def test_scrape_valid_only_form(scraper_class, filename, mimetype):
    """Test cases of Jhove scraping"""
    file_path = os.path.join(TESTDATADIR_BASE, filename)
    scraper = scraper_class(file_path, mimetype)
    scraper.scrape_file()
    assert scraper.well_formed, scraper.errors()
    assert "Well-Formed and valid" in scraper.messages()
    assert scraper.errors() == ""


@pytest.mark.parametrize(
    ["scraper_class", "filename", "mimetype", "stdout"],
    [
        (HtmlJHove, "text_html/invalid_4.htm",
         "text/html", "Well-Formed, but not valid"),
        (GifJHove, "image_gif/invalid_1987a.gif",
         "image/gif", "Not well-formed"),
        (GifJHove, "image_gif/invalid_1989a.gif",
         "image/gif", "Not well-formed"),
        (PdfJHove, "application_pdf/pdfa1-fail.pdf",
         "application/pdf", "Not well-formed"),
        (TiffJHove, "image_tiff/invalid_6.0.tif",
         "image/tiff", "Not well-formed"),
        (Utf8JHove, "text_plain/iso8859.txt",
         "text/plain", "Not well-formed"),
        (WavJHove,
         "audio_x-wav/invalid_wav_last_byte_missing.wav",
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
