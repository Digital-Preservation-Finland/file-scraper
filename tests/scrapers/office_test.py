"""
Tests for Office scraper.
"""

import os
import pytest
from multiprocessing import Pool
from dpres_scraper.scrapers.office import Office

BASEPATH = "tests/data"


@pytest.mark.parametrize(
    ['filename', 'mimetype'],
    [
        ("valid_1.1.odt", "application/vnd.oasis.opendocument.text"),
        ("valid_11.0.doc", "application/msword"),
        ("valid_15.0.docx", "application/vnd.openxmlformats-"
         "officedocument.wordprocessingml.document"),
        ("valid_1.1.odp",
         "application/vnd.oasis.opendocument.presentation"),
        ("valid_11.0.ppt", "application/vnd.ms-powerpoint"),
        ("valid_15.0.pptx", "application/vnd.openxml"
         "formats-officedocument.presentationml.presentation"),
        ("valid_1.1.ods",
         "application/vnd.oasis.opendocument.spreadsheet"),
        ("valid_11.0.xls", "application/vnd.ms-excel"),
        ("valid_15.0.xlsx", "application/vnd."
         "openxmlformats-officedocument.spreadsheetml.sheet"),
        ("valid_1.1.odg", "application/vnd.oasis.opendocument.graphics"),
        ("valid_1.0.odf", "application/vnd.oasis.opendocument.formula"),
    ]
)
def test_scrape_valid_file(filename, mimetype):
    assert _scrape(filename, mimetype)

@pytest.mark.parametrize(
    ['filename', 'mimetype'],
    [
        # Corrupted file
        ("ODF_Text_Document_corrupted.odt",
         "application/vnd.oasis.opendocument.text"),
        # .zip renamed to .docx
        ("MS_Word_2007-2013_XML_zip.docx", "application/vnd.openxmlformats-"
         "officedocument.wordprocessingml.document"),
    ]
)
def test_scrape_invalid_file(filename, mimetype):
    assert not _scrape(filename, mimetype)


def _scrape(filename, mimetype):
    scraper = Office(os.path.join(BASEPATH, mimetype.replace('/', '_'),
                                  filename), mimetype)
    scraper.scrape_file()
    return scraper.well_formed


@pytest.mark.parametrize(
    ['filename', 'mimetype'],
    [
        ("valid_1.1.odt", "application/vnd.oasis.opendocument.text"),
    ]
)
def test_parallel_validation(filename, mimetype):
    """Test validation in parallel. Libreoffice convert command is prone for
    freezing which would cause TimeOutError here.
    """

    n = 3
    pool = Pool(n)
    results = [pool.apply_async(_scrape, (filename, mimetype)) for i in range(n)]

    for result in results:
        assert result.get(timeout=3)
