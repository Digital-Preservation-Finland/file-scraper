"""
Tests for ImageMagick scraper.
"""

import os
import pytest
from dpres_scraper.scrapers.wand import TiffWand, ImageWand


BASEPATH = "tests/data/02_filescraping_data/imagemagick"


@pytest.mark.parametrize(
    ['filename', 'mimetype', 'class_'],
    [
        ("valid_jpeg.jpeg", "image/jpeg", ImageWand),
        ("valid_jp2.jp2", "image/jp2", ImageWand),
        ("valid_tiff.tiff", "image/tiff", TiffWand),
        ("valid_png.png", "image/png", ImageWand),
    ]
)
def test_scrape_valid_file(filename, mimetype, class_):

    scraper = class_(os.path.join(BASEPATH, filename), mimetype)
    scraper.scrape_file()
    assert scraper.well_formed


@pytest.mark.parametrize(
    ['filename', 'mimetype'],
    [
        ("valid_png.png", "image/tiff")
    ]
)
def test_scrape_invalid_file(filename, mimetype):

    scraper = ImageWand(os.path.join(BASEPATH, filename), mimetype)
    scraper.scrape_file()
    assert not scraper.well_formed
