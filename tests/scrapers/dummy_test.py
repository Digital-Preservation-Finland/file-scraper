"""Test module for dummy.py

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

from file_scraper.scrapers.dummy import ScraperNotFound, FileExists

DEFAULTSTREAMS = {0: {'index': 0, 'version': None,
                      'stream_type': None}}


@pytest.mark.parametrize(
    ["filepath", "mimetype"],
    [
        ("tests/data/image_gif/valid_1987a.gif", "image/gif"),
        ("tests/data/image_gif/invalid_1987a_broken_header.gif",
         "image/gif"),
        ("tests/data/image_gif/invalid__empty.gif", "image/gif"),
        ("tests/data/application_pdf/valid_1.4.pdf", "application/pdf")
    ]
)
def test_existing_files(filepath, mimetype):
    """Test that existent files are identified correctly."""

    scraper = FileExists(filepath, mimetype, True)
    scraper.scrape_file()

    streams = DEFAULTSTREAMS.copy()
    streams[0]['mimetype'] = mimetype

    assert scraper.well_formed is None
    assert not scraper.errors()
    assert "was found" in scraper.messages()
    assert scraper.mimetype == mimetype
    assert scraper.version is None
    assert scraper.streams == streams
    assert scraper.info['class'] == 'FileExists'


@pytest.mark.parametrize(
    ["filepath", "mimetype"],
    [
        ("tests/data/image_gif/nonexistent_file.gif", "image/gif"),
        ("tests/data/nonexistent_dir/nonexistent_file.txt", "no/mime")
    ]
)
def test_nonexistent_files(filepath, mimetype):
    """Test that non-existent files are identified correctly."""
    scraper = FileExists(filepath, mimetype, True)
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
    ["filepath", "mimetype"],
    [
        ("tests/data/image_gif/valid_1987a.gif", "image/gif"),
        ("tests/data/image_gif/valid_1987a.gif", "wrong/mime"),
        ("tests/data/image_gif/invalid_1987a_truncated.gif", "image/gif"),
        ("tests/data/video_x-matroska/valid__ffv1.mkv", "video/x-matroska")
    ]
)
def test_scraper_not_found(filepath, mimetype):
    """Check ScraperNotFound results."""
    scraper = ScraperNotFound(filepath, mimetype, True)
    scraper.scrape_file()

    streams = DEFAULTSTREAMS.copy()
    streams[0]['mimetype'] = mimetype

    assert scraper.well_formed is None
    assert scraper.mimetype == mimetype
    assert scraper.version is None
    assert scraper.streams == streams
    assert scraper.info['class'] == 'ScraperNotFound'
