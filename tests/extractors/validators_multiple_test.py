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


def test_scrape_wrong_predefined_mimetype():
    """Test extracting a file with wrong predefined mimetype.

    A valid odt file with application/mdword as predefined mimetype.
    OfficeExtractor will extract the file because it supports also
    msword files, and therefore it it reports the file as well-formed.
    However, it should report the actual mimetype of file, which is not
    the predefined mimetype. This will cause conflict when extractor
    results are merged, but it is not tested here.

    """
    extractor_results = []
    extractor_errors = []
    extractor_mimetypes = []
    predefined_mimetype="application/msword"
    for extractor in iter_extractors(
        Path("tests/data/application_vnd.oasis.opendocument.text/"
             "valid_1.2.odt"),
        mimetype=predefined_mimetype,
        version="97-2003",
        charset=None,
    ):
        extractor.extract()
        extractor_results.append(extractor.well_formed)
        extractor_errors += extractor.errors()
        extractor_mimetypes.append(extractor.streams[0].mimetype())

    assert False not in extractor_results
    assert not extractor_errors
    assert "application/vnd.oasis.opendocument.text" in extractor_mimetypes
    assert predefined_mimetype not in extractor_mimetypes
