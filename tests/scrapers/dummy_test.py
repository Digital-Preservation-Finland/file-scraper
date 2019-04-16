"""
Test module for dummy.py

This module tests the following scraper classes:
    - ScraperNotFound
        - Existing files, both well-formed and non-well-formed, are found and
          their mimetype and streams are identified correctly whereas version
          and well_formed should be reported as None. No errors should be
          recorded.
        - Non-existent files are reported as not well-formed and the fact that
          the file does not exist is recorded in scraper errors. This behaviour
          is independent of the given MIME type.
        - Giving None as file path results in 'No filename given' being
          reported in the scraper errors and well_formed is False.
    - ScraperNotFound
        - version and well_formed are None.
        - MIME type is what is given to the scraper.
        - Streams contain only one dict with version and stream_type as None
          and MIME type as what was given to the scraper.
"""

import pytest

from file_scraper.dummy.dummy_scraper import ScraperNotFound, FileExists

DEFAULTSTREAMS = {0: {"index": 0, "version": "(:unav)",
                      "stream_type": None, "mimetype": "(:unav)"}}


@pytest.mark.parametrize(
    "filepath",
    [
        "tests/data/image_gif/valid_1987a.gif",
        "tests/data/image_gif/invalid_1987a_broken_header.gif",
        "tests/data/image_gif/invalid__empty.gif",
        "tests/data/application_pdf/valid_1.4.pdf"
    ]
)
def test_existing_files(filepath):
    """Test that existent files are identified correctly."""

    scraper = FileExists(filepath, True)
    scraper.scrape_file()

    streams = DEFAULTSTREAMS.copy()

    assert scraper.well_formed is None
    assert not scraper.errors()
    assert "was found" in scraper.messages()
    assert scraper.info()["class"] == "FileExists"
    for stream_index, stream_metadata in streams.iteritems():
        scraped_metadata = scraper.streams[stream_index]
        for key, value in stream_metadata.iteritems():
            print key
            assert getattr(scraped_metadata, key)() == value


@pytest.mark.parametrize(
    "filepath", "tests/data/image_gif/nonexistent_file.gif"
)
def test_nonexistent_files(filepath):
    """Test that non-existent files are identified correctly."""
    scraper = FileExists(filepath, True)
    scraper.scrape_file()

    assert not scraper.well_formed
    assert "does not exist" in scraper.errors()


def test_none_filename():
    """Test that giving None filename results in error."""
    scraper = FileExists(None, None)
    scraper.scrape_file()

    assert not scraper.well_formed
    assert "No filename given." in scraper.errors()


@pytest.mark.parametrize(
    "filepath",
    [
        "tests/data/image_gif/valid_1987a.gif",
        "tests/data/image_gif/valid_1987a.gif",
        "tests/data/image_gif/invalid_1987a_truncated.gif",
        "tests/data/video_x-matroska/valid__ffv1.mkv"
    ]
)
def test_scraper_not_found(filepath):
    """Check ScraperNotFound results."""
    scraper = ScraperNotFound(filepath, True)
    scraper.scrape_file()

    streams = DEFAULTSTREAMS.copy()

    assert scraper.well_formed is None
    for stream_index, stream_metadata in streams.iteritems():
        scraped_metadata = scraper.streams[stream_index]
        for key, value in stream_metadata.iteritems():
            print key
            assert getattr(scraped_metadata, key)() == value
