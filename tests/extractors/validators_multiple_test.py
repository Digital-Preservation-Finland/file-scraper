"""
Tests office-file scraping with Office-extractor.

This module tests that:
    - For a well-formed odt file, all extractors supporting
      application/vnd.oasis.opendocument.text version 1.2 report it as
      well-formed or None.
    - For a corrupted odt file, at least one extractor supporting
      application/vnd.oasis.opendocument.text reports it as not well-formed.
    - When a valid odt file is scraped with extractors selected using wrong MIME
      type (application/msword) at least one of them reports it as not well-
      formed.
"""

from pathlib import Path

import pytest

from file_scraper.iterator import iter_extractors

BASEPATH = "tests/data"


def test_scrape_valid_file():
    """Test extracting a well-formed odt file."""
    path=Path("tests/data/application_vnd.oasis.opendocument.text/valid_1.2.odt")
    mimetype="application/vnd.oasis.opendocument.text"
    for extractor in iter_extractors(
        path=path,
        mimetype=mimetype,
        version=None,
        charset=None,
    ):
        extractor.extract()
        assert extractor.well_formed in [True, None]


def test_scrape_invalid_file():
    """Test extracting an invalid odt file.

    At least one extractor (OfficeExtractor), should notice that the
    file is not well-formed.
    """
    extractor_results = []
    extractor_errors = []
    for extractor in iter_extractors(
        path=Path("tests/data/application_vnd.oasis.opendocument.text/"
                  "invalid_1.2_corrupted.odt"),
        mimetype="application/vnd.oasis.opendocument.text",
        version="1.2",
        charset=None,
    ):
        extractor.extract()
        extractor_results.append(extractor.well_formed)
        extractor_errors += extractor.errors()

    assert False in extractor_results
    assert "Error: source file could not be loaded\n" in extractor_errors
