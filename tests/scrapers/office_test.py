"""
Tests for Office scraper.
"""

import os
import pytest
from multiprocessing import Pool
from dpres_scraper.scrapers.office import Office

BASEPATH = "tests/data/documents"

@pytest.mark.parametrize(
    ['filename', 'mimetype'],
    [
        ("ODF_Text_Document.odt", "application/vnd.oasis.opendocument.text"),
        ("ODF_Text_Document.odt", "application/vnd.oasis.opendocument.text"),
        ("MS_Word_97-2003.doc", "application/msword"),
        ("Office_Open_XML_Text.docx", "application/vnd.openxmlformats-"
         "officedocument.wordprocessingml.document"),
        ("ODF_Presentation.odp",
         "application/vnd.oasis.opendocument.presentation"),
        ("MS_PowerPoint_97-2003.ppt", "application/vnd.ms-powerpoint"),
        ("Office_Open_XML_Presentation.pptx", "application/vnd.openxml"
         "formats-officedocument.presentationml.presentation"),
        ("ODF_Spreadsheet.ods",
         "application/vnd.oasis.opendocument.spreadsheet"),
        ("MS_Excel_97-2003.xls", "application/vnd.ms-excel"),
        ("Excel_Online_Spreadsheet.xlsx",
         "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"),
        ("ODF_Drawing.odg", "application/vnd.oasis.opendocument.graphics"),
        ("ODF_Formula.odf", "application/vnd.oasis.opendocument.formula"),
        ("Office_Open_XML_Spreadsheet.xlsx", "application/vnd."
         "openxmlformats-officedocument.spreadsheetml.sheet"),
        ("ODF_Text_Document.odt", "application/msword"),
        ("ODF_Text_Document_with_wrong_filename_extension.doc",
         "application/msword"),
        ("MS_Word_97-2003.doc", "application/msword"),
        ("ODF_Text_Document.odt",
         "application/vnd.oasis.opendocument.text"),
    ]
)
def test_scrape_valid_file(filename, mimetype):
    scraper = Office(os.path.join(BASEPATH, filename), mimetype)
    scraper.scrape_file()
    assert scraper.well_formed


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
    scraper = Office(os.path.join(BASEPATH, filename), mimetype)
    scraper.scrape_file()
    assert not scraper.well_formed


def _scrape(filename, mimetype):
    scraper = Office(os.path.join(BASEPATH, filename), mimetype)
    scraper.scrape_file()
    return scraper.well_formed


@pytest.mark.parametrize(
    ['filename', 'mimetype'],
    [
        ("ODF_Text_Document.odt", "application/vnd.oasis.opendocument.text"),
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
