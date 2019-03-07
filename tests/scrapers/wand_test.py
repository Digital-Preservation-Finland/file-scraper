"""
Tests for ImageMagick scraper.
"""

import os
import pytest
from dpres_scraper.scrapers.wand import TiffWand, ImageWand


BASEPATH = "tests/data/images"


@pytest.mark.parametrize(
    ['filename', 'mimetype', 'class_'],
    [
        ("valid_1.01.jpg", "image/jpeg", ImageWand),
        ("valid.jp2", "image/jp2", ImageWand),
        ("valid_6.0.tif", "image/tiff", TiffWand),
        ("valid_1.2.png", "image/png", ImageWand),
    ]
)
def test_scrape_valid_file(filename, mimetype, class_):

    scraper = class_(os.path.join(BASEPATH, filename), mimetype)
    scraper.scrape_file()
    assert scraper.well_formed


@pytest.mark.parametrize(
    ['filename', 'mimetype'],
    [
        ("invalid_1.2.png", "image/png")
    ]
)
def test_scrape_invalid_file(filename, mimetype):

    scraper = ImageWand(os.path.join(BASEPATH, filename), mimetype)
    scraper.scrape_file()
    assert not scraper.well_formed
