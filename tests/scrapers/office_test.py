"""
Tests for Office scraper.
"""

import os
from multiprocessing import Pool
import pytest
from file_scraper.scrapers.office import Office
from tests.common import parse_results


BASEPATH = 'tests/data'


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
def test_scraper_valid_file(filename, mimetype):
    """Test valid files with scraper"""
    result_dict = {
        'purpose': 'Test valid file.',
        'stdout_part': '',
        'stderr_part': ''}
    correct = parse_results(filename, mimetype,
                            result_dict, True)
    scraper = Office(correct.filename, correct.mimetype,
                     True, correct.params)
    scraper.scrape_file()
    correct.version = None
    correct.streams[0]['version'] = None

    assert scraper.mimetype == correct.mimetype
    assert scraper.version == correct.version
    assert scraper.streams == correct.streams
    assert scraper.info['class'] == 'Office'
    assert len(scraper.messages()) > 0
    assert len(scraper.errors()) == 0
    assert scraper.well_formed == correct.well_formed


@pytest.mark.parametrize(
    ['filename', 'mimetype'],
    [
        ("invalid_1.1_corrupted.odt", "application/vnd.oasis.opendocument"
         ".text"),
        ("invalid_15.0_corrupted.docx", "application/vnd.openxmlformats-"
         "officedocument.wordprocessingml.document"),
        ("invalid_1.1_corrupted.odp",
         "application/vnd.oasis.opendocument.presentation"),
        ("invalid_15.0_corrupted.pptx", "application/vnd.openxml"
         "formats-officedocument.presentationml.presentation"),
        ("invalid_1.1_corrupted.ods",
         "application/vnd.oasis.opendocument.spreadsheet"),
        ("invalid_15.0_corrupted.xlsx", "application/vnd."
         "openxmlformats-officedocument.spreadsheetml.sheet"),
        ("invalid_1.1_corrupted.odg", "application/vnd.oasis.opendocument"
         ".graphics"),
        ("invalid_1.0_corrupted.odf", "application/vnd.oasis.opendocument"
         ".formula"),
    ]
)
def test_scraper_invalid_file(filename, mimetype):
    """Test scraper with invalid files."""
    result_dict = {
        'purpose': 'Test invalid file.',
        'stdout_part': '',
        'stderr_part': 'source file could not be loaded'}
    correct = parse_results(filename, mimetype,
                            result_dict, True)
    scraper = Office(correct.filename, correct.mimetype,
                     True, correct.params)
    scraper.scrape_file()
    correct.version = None
    correct.streams[0]['version'] = None

    assert scraper.mimetype == correct.mimetype
    assert scraper.version == correct.version
    assert scraper.streams == correct.streams
    assert scraper.info['class'] == 'Office'
    assert correct.stdout_part in scraper.messages()
    assert correct.stderr_part in scraper.errors()
    assert scraper.well_formed == correct.well_formed


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

    number = 3
    pool = Pool(number)
    results = [pool.apply_async(_scrape, (filename, mimetype))
               for _ in range(number)]

    for result in results:
        assert result.get(timeout=3)
