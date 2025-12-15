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

import os
import pytest
from file_scraper.iterator import iter_extractors

BASEPATH = "tests/data"


# Test valid file
@pytest.mark.parametrize(
    ['filename', 'mimetype'],
    [
        ("valid_1.2.odt", "application/vnd.oasis.opendocument.text"),
    ]
)
def test_scrape_valid_file(filename, mimetype):
    """
    Test scraping for a well-formed odt file.

    :filename: Test file name
    :mimetype: File MIME type
    """
    for class_ in iter_extractors(mimetype, None):
        extractor = class_(
            filename=os.path.join(BASEPATH, mimetype.replace('/', '_'),
                                  filename),
            mimetype=mimetype)
        extractor.extract()
        assert extractor.well_formed in [True, None]


# Test invalid files
@pytest.mark.parametrize(
    ['filename', 'mimetype'],
    [
        # Corrupted file - caught by Office extractor
        ("ODF_Text_Document_corrupted.odt",
         "application/vnd.oasis.opendocument.text"),
        # Wrong MIME
        ("valid_1.2.odt", "application/msword"),
    ]
)
def test_scrape_invalid_file(filename, mimetype):
    """
    Test scraping for invalid files.

    :filename: Test file name
    :mimetype: File MIME type
    """
    extractor_results = []
    for class_ in iter_extractors(mimetype, None):
        extractor = class_(
            filename=os.path.join(
                BASEPATH, "application_vnd.oasis.opendocument.text", filename),
            mimetype=mimetype)
        extractor.extract()
        extractor_results.append(extractor.well_formed)

    assert not all(extractor_results)
    assert extractor_results
