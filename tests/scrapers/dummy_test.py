"""Test module for dummy.py"""

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
        ("tests/data/image_gif/invalid__empty.gif", "image/gif")
    ]
)
def test_existing_files(filepath, mimetype):
    """Test that existent and files are identified correctly."""

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
    assert scraper.well_formed is None


@pytest.mark.parametrize(
    ["filepath", "mimetype"],
    [
        ("tests/data/image_gif/nonexistent_file.gif", "image/gif"),
        ("tests/data/nonexistent_dir/nonexistent_file.txt", "no/mime")
    ]
)
def test_nonexistent_files(filepath, mimetype):
    """Test that non-existent files are identified correctly"""
    scraper = FileExists(filepath, mimetype, True)
    scraper.scrape_file()

    assert not scraper.well_formed
    assert "does not exist" in scraper.errors()


def test_none_filename():
    """Test that None filename results error"""
    scraper = FileExists(None, None)
    scraper.scrape_file()

    assert not scraper.well_formed
    assert "No filename given." in scraper.errors()


@pytest.mark.parametrize(
    ["filepath", "mimetype"],
    [
        ("tests/data/image_gif/valid_1987a.gif", "image/gif"),
        ("tests/data/video_x-matroska/valid__ffv1.mkv", "video/x-matroska")
    ]
)
def test_scraper_not_found(filepath, mimetype):
    """Check ScraperNotFound results"""
    scraper = ScraperNotFound(filepath, mimetype, True)
    scraper.scrape_file()

    streams = DEFAULTSTREAMS.copy()
    streams[0]['mimetype'] = mimetype

    assert scraper.well_formed is None
    assert scraper.mimetype == mimetype
    assert scraper.version is None
    assert scraper.streams == streams
    assert scraper.info['class'] == 'ScraperNotFound'
    assert scraper.well_formed is None
