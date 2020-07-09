# -*- coding: UTF-8 -*-

"""
Tests for Csv scraper

This module tests that:
    - mimetype, version and streams are scraped correctly when a csv file is
      scraped.
    - scraper class used for csv scraping is CsvScraper.
    - well-formedness of csv files is determined accurately.
    - scraper reports errors in scraping as expected when there is a missing
      quote or wrong field delimiter is given.
    - scraping a file other than csv file results in:
        - not well-formed
        - success not reported in scraper messages
        - some error recorded by the scraper
    - scraper is able to extract the MIME type of a well-formed file and
      guess the file as a well-formed one also when separator, delimiter
      and fields are not given by user.
    - all files with MIME type 'text/csv' are reported to be supported
      and for empty, None or arbitrary string as the version.
    - MIME type other than 'text/csv' is not supported.
    - Not giving CsvMeta enough parameters causes an error to be raised.
    - Empty file is not well-formed.
    - Sniffer is not used when giving the delimiter and separator as a
      parameter.
    - Non-existent files are not well-formed and the inability to read the
      file is logged as an error.
"""
from __future__ import unicode_literals

import os
import pytest
import six

from file_scraper.csv.csv_model import CsvMeta
from file_scraper.csv.csv_scraper import CsvScraper
from file_scraper.defaults import UNAP, UNAV
from tests.common import parse_results, partial_message_included

MIMETYPE = "text/csv"

PDF_PATH = os.path.join(
    "tests/data/application_pdf/valid_1.4.pdf")

TEST_DATA_PATH = "tests/data/text_csv"


# pylint: disable=too-many-arguments
@pytest.mark.parametrize(
    ["filename", "result_dict", "header", "extra_params"],
    [
        ("valid__ascii.csv", {
            "purpose": "Test valid file.",
            "stdout_part": "successfully",
            "stderr_part": "",
            "streams": {0: {"stream_type": "text",
                            "index": 0,
                            "mimetype": MIMETYPE,
                            "version": UNAP,
                            "delimiter": ",",
                            "separator": "\n",
                            "first_line": ["1997", "Ford", "E350",
                                           "ac, abs, moon",
                                           "3000.00"]}}},
         None, {}),
        ("valid__ascii_header.csv", {
            "purpose": "Test valid file with header.",
            "stdout_part": "successfully",
            "stderr_part": "",
            "streams": {0: {"stream_type": "text",
                            "index": 0,
                            "mimetype": MIMETYPE,
                            "version": UNAP,
                            "delimiter": ",",
                            "separator": "\n",
                            "first_line": ["year", "brand", "model", "detail",
                                           "other"]}}},
         ["year", "brand", "model", "detail", "other"], {}),
        ("invalid__missing_end_quote.csv", {
            "purpose": "Test missing end quote",
            "stdout_part": "",
            "stderr_part": "unexpected end of data",
            "streams": {0: {"stream_type": UNAV,
                            "index": 0,
                            "mimetype": UNAV,
                            "version": UNAV,
                            "delimiter": ",",
                            "separator": "\n",
                            "first_line": ["1997", "Ford", "E350",
                                           "ac, abs, moon",
                                           "3000.00"]}}},
         None, {}),
        ("valid__header_only.csv", {
            "purpose": "Test file containing only the header without any data",
            "stdout_part": "successfully",
            "stderr_part": "",
            "streams": {0: {"stream_type": "text",
                            "index": 0,
                            "mimetype": MIMETYPE,
                            "version": UNAP,
                            "delimiter": ";",
                            "separator": "\n",
                            "first_line": ["year,brand,model,detail,other"]}}},
         ["year,brand,model,detail,other"], {}),
        ("valid__ascii_header.csv", {
            "purpose": "Invalid delimiter",
            "inverse": True,
            "stdout_part": "",
            "stderr_part": "CSV not well-formed: field counts",
            "streams": {0: {"stream_type": UNAV,
                            "index": 0,
                            "mimetype": UNAV,
                            "version": UNAV,
                            "delimiter": ";",
                            "separator": "\n",
                            "first_line": ["year,brand,model,detail,other"]}}},
         ["year", "brand", "model", "detail", "other"], {}),
        ("valid__iso8859-15.csv", {
            "purpose": "Non-ASCII characters",
            "stdout_part": "successfully",
            "stderr_part": "",
            "streams": {0: {"stream_type": "text",
                            "index": 0,
                            "mimetype": MIMETYPE,
                            "version": UNAP,
                            "delimiter": ";",
                            "separator": "\n",
                            "first_line": ["year,brand,model,detail,other"]}}},
         ["year,brand,model,detail,other"], {"charset": "iso8859-15"}),
        ("valid__utf8.csv", {
            "purpose": "Non-ASCII characters",
            "stdout_part": "successfully",
            "stderr_part": "",
            "streams": {0: {"stream_type": "text",
                            "index": 0,
                            "mimetype": MIMETYPE,
                            "version": UNAP,
                            "delimiter": ";",
                            "separator": "\n",
                            "first_line": ["year,brand,model,detail,other"]}}},
         ["year,brand,model,detail,other"], {"charset": "utf-8"})
    ]
)
def test_scraper(filename, result_dict, header,
                 extra_params, evaluate_scraper):
    """
    Write test data and run csv scraping for the file.

    :filename: Test file name
    :result_dict: Result dict containing purpose of the test, parts of
                  expected stdout and stderr, and expected streams
    :header: CSV header line
    :extra_params: Extra parameters for the scraper (e.g. charset)
    """
    correct = parse_results(filename, "text/csv", result_dict,
                            True)
    params = {
        "separator": correct.streams[0]["separator"],
        "delimiter": correct.streams[0]["delimiter"],
        "fields": header,
        "mimetype": "text/csv"}
    params.update(extra_params)
    scraper = CsvScraper(filename=correct.filename, mimetype=MIMETYPE,
                         params=params)
    scraper.scrape_file()

    evaluate_scraper(scraper, correct)


@pytest.mark.parametrize("filename, charset", [
    ("tests/data/text_csv/valid__utf8_header.csv", "UTF-8"),
    ("tests/data/text_csv/valid__iso8859-15_header.csv", "ISO-8859-15"),
])
def test_first_line_charset(filename, charset):
    """
    Test that CSV handles the first line encoding correctly.

    :filename: Test file name
    :charset: Character encoding
    """
    params = {"delimiter": ",", "separator": "CR+LF",
              "mimetype": "text/csv", "charset": charset}

    scraper = CsvScraper(filename, mimetype="text/csv", params=params)
    scraper.scrape_file()
    assert scraper.well_formed
    assert scraper.streams[0].first_line() == \
        ["year", "bränd", "mödel", "detail", "other"]


def test_pdf_as_csv():
    """Test CSV scraper with PDF files."""
    scraper = CsvScraper(filename=PDF_PATH, mimetype="text/csv")
    scraper.scrape_file()

    assert not scraper.well_formed, scraper.messages() + scraper.errors()
    assert not partial_message_included("successfully", scraper.messages())
    assert scraper.errors()


@pytest.mark.parametrize(
    "filename",
    [
        ("valid__utf8.csv"),
        ("valid__ascii_header.csv")
    ]
)
def test_no_parameters(filename, evaluate_scraper):
    """
    Test scraper without separate parameters.

    :filename: Test file name
    """
    correct = parse_results(filename, MIMETYPE,
                            {"purpose": "Test valid file on default settings.",
                             "stdout_part": "successfully",
                             "stderr_part": "",
                             "streams":
                             {0: {"stream_type": "text",
                                  "index": 0,
                                  "mimetype": MIMETYPE,
                                  "version": UNAP,
                                  "delimiter": ",",
                                  "separator": "\r\n",
                                  "first_line": ["year", "brand", "model",
                                                 "detail", "other"]}}},
                            True)
    scraper = CsvScraper(correct.filename, mimetype="text/csv")
    scraper.scrape_file()
    evaluate_scraper(scraper, correct)


def test_bad_parameters():
    """
    Test that CsvMeta raises an error if proper parameters are not given.
    """
    with pytest.raises(ValueError) as err:
        # "separator" is missing from the keys
        CsvMeta(well_formed=True, params={"delimiter": ",", "fields": [],
                                          "first_line": ""})
    assert ("CsvMeta must be given a dict containing keys" in
            six.text_type(err.value))


def test_empty_file():
    """
    Test empty file, and that sniffer is not used if delimiter and
    separator are given.

    We first test with empty file that sniffer raises exception if the
    parameters are not given. Secondly, sniffer is skipped when parameters
    are given, but the then scraper raises exception elsewhere.
    """
    scraper = CsvScraper("tests/data/text_csv/invalid__empty.csv",
                         mimetype=MIMETYPE)
    scraper.scrape_file()
    assert partial_message_included("Could not determine delimiter",
                                    scraper.errors())
    assert not scraper.well_formed

    scraper = CsvScraper("tests/data/text_csv/invalid__empty.csv",
                         mimetype=MIMETYPE,
                         params={"delimiter": ";", "separator": "CRLF"})
    scraper.scrape_file()
    assert partial_message_included("Error reading file as CSV",
                                    scraper.errors())
    assert not scraper.well_formed


def test_nonexistent_file():
    """
    Test that CsvScraper logs an error when file is not found.
    """
    scraper = CsvScraper(filename="nonexistent/file.csv", mimetype="text/csv")
    scraper.scrape_file()
    assert partial_message_included("Error when reading the file: ",
                                    scraper.errors())
    assert not scraper.well_formed


def test_is_supported():
    """Test is_supported method."""
    mime = MIMETYPE
    ver = ""
    assert CsvScraper.is_supported(mime, ver, True)
    assert CsvScraper.is_supported(mime, None, True)
    assert CsvScraper.is_supported(mime, ver, False)
    assert CsvScraper.is_supported(mime, "foo", True)
    assert not CsvScraper.is_supported("foo", ver, True)
