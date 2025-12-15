"""
Tests for Csv extractor

This module tests that:
    - mimetype, version and streams are scraped correctly when a csv file is
      scraped.
    - extractor class used for csv scraping is CsvExtractor.
    - well-formedness of csv files is determined accurately.
    - extractor reports errors in scraping as expected when there is a missing
      quote or wrong field delimiter is given.
    - scraping a file other than csv file results in:
        - not well-formed
        - success not reported in extractor messages
        - some error recorded by the extractor
    - extractor is able to extract the MIME type of a well-formed file and
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

import os
from pathlib import Path

import pytest

from file_scraper.csv_extractor.csv_model import CsvMeta
from file_scraper.csv_extractor.csv_extractor import CsvExtractor
from file_scraper.defaults import UNAP, UNAV
from tests.common import parse_results, partial_message_included

MIMETYPE = "text/csv"

PDF_PATH = Path(
    "tests/data/application_pdf/valid_1.4.pdf")

TEST_DATA_PATH = "tests/data/text_csv"


# pylint: disable=too-many-arguments
@pytest.mark.parametrize(
    ["filename", "result_dict", "header", "extra_params"],
    [
        ("valid__ascii.csv", {
            "purpose": "Test valid file.",
            "stdout_part": "The file was analyzed",
            "stderr_part": "",
            "streams": {0: {"stream_type": "text",
                            "index": 0,
                            "mimetype": MIMETYPE,
                            "version": UNAP,
                            "delimiter": ",",
                            "separator": "\n",
                            "quotechar": "\"",
                            "first_line": ["1997", "Ford", "E350",
                                           "ac, abs, moon",
                                           "3000.00"]}}},
         None, {}),
        ("valid__quotechar.csv", {
            "purpose": "Test different quote character.",
            "stdout_part": "The file was analyzed",
            "stderr_part": "",
            "streams": {0: {"stream_type": "text",
                            "index": 0,
                            "mimetype": MIMETYPE,
                            "version": UNAP,
                            "delimiter": ",",
                            "separator": "\n",
                            "quotechar": "|",
                            "first_line": ["1997", "Ford", "E350",
                                           "ac, abs, moon",
                                           "3000.00"]}}},
         None, {"quotechar": "|"}),
        ("valid__ascii_header.csv", {
            "purpose": "Test valid file with header.",
            "stdout_part": "The file was analyzed",
            "stderr_part": "",
            "streams": {0: {"stream_type": "text",
                            "index": 0,
                            "mimetype": MIMETYPE,
                            "version": UNAP,
                            "delimiter": ",",
                            "separator": "\n",
                            "quotechar": "\"",
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
                            "quotechar": "\"",
                            "first_line": ["1997", "Ford", "E350",
                                           "ac, abs, moon",
                                           "3000.00"]}}},
         None, {}),
        ("valid__header_only.csv", {
            "purpose": "Test file containing only the header without any data",
            "stdout_part": "The file was analyzed",
            "stderr_part": "",
            "streams": {0: {"stream_type": "text",
                            "index": 0,
                            "mimetype": MIMETYPE,
                            "version": UNAP,
                            "delimiter": ";",
                            "separator": "\n",
                            "quotechar": "\"",
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
                            "quotechar": "\"",
                            "first_line": ["year,brand,model,detail,other"]}}},
         ["year", "brand", "model", "detail", "other"], {}),
        ("valid__iso8859-15.csv", {
            "purpose": "Non-ASCII characters",
            "stdout_part": "The file was analyzed",
            "stderr_part": "",
            "streams": {0: {"stream_type": "text",
                            "index": 0,
                            "mimetype": MIMETYPE,
                            "version": UNAP,
                            "delimiter": ";",
                            "separator": "\n",
                            "quotechar": "\"",
                            "first_line": ["year,brand,model,detail,other"]}}},
         ["year,brand,model,detail,other"], {"charset": "iso8859-15"}),
        ("valid__utf8.csv", {
            "purpose": "Non-ASCII characters",
            "stdout_part": "The file was analyzed",
            "stderr_part": "",
            "streams": {0: {"stream_type": "text",
                            "index": 0,
                            "mimetype": MIMETYPE,
                            "version": UNAP,
                            "delimiter": ";",
                            "separator": "\n",
                            "quotechar": "\"",
                            "first_line": ["year,brand,model,detail,other"]}}},
         ["year,brand,model,detail,other"], {"charset": "utf-8"})
    ]
)
def test_extractor(filename, result_dict, header,
                 extra_params, evaluate_extractor):
    """
    Write test data and run csv scraping for the file.

    :filename: Test file name
    :result_dict: Result dict containing purpose of the test, parts of
                  expected stdout and stderr, and expected streams
    :header: CSV header line
    :extra_params: Extra parameters for the extractor (e.g. charset)
    """
    correct = parse_results(filename, "text/csv", result_dict,
                            True)
    params = {
        "separator": correct.streams[0]["separator"],
        "delimiter": correct.streams[0]["delimiter"],
        "fields": header,
        "mimetype": MIMETYPE}
    params.update(extra_params)
    extractor = CsvExtractor(filename=correct.filename, mimetype=MIMETYPE,
                           params=params)
    extractor.extract()

    evaluate_extractor(extractor, correct)


@pytest.mark.parametrize(
    ["filename", "result_dict", "header", "extra_params", "size"],
    [
        ("valid__large_field.csv", {
            "purpose": "Test valid file with a large field.",
            "stdout_part": "The file was analyzed",
            "stderr_part": "",
            "streams": {0: {"stream_type": "text",
                            "index": 0,
                            "mimetype": MIMETYPE,
                            "version": UNAP,
                            "delimiter": ",",
                            "separator": "\n",
                            "quotechar": "\"",
                            "first_line": ["test1", "test2"]}}},
         None, {}, 1048500),
        ("invalid__too_large_field.csv", {
            "purpose": "Test a file with too large field.",
            "stdout_part": "",
            "stderr_part": "field larger than field limit",
            "streams": {0: {"stream_type": UNAV,
                            "index": 0,
                            "mimetype": UNAV,
                            "version": UNAV,
                            "delimiter": ",",
                            "separator": "\n",
                            "quotechar": "\"",
                            "first_line": ["test1", "test2"]}}},
         None, {}, 1048600),
    ]
)
def test_large_field(filename, result_dict, header,
                     extra_params, size,
                     evaluate_extractor, tmpdir):
    """
    Test that large field sizes are properly handled.
    Large test files are created on the fly so as not to take up space.

    :filename: Test file name
    :result_dict: Result dict containing purpose of the test, parts of
                  expected stdout and stderr, and expected streams
    :header: CSV header line
    :extra_params: Extra parameters for the extractor (e.g. charset)
    :size: Amount of bytes in the large field
    """
    tempdatapath = os.path.join(tmpdir, "text_csv")
    os.makedirs(tempdatapath)
    tempfilepath = os.path.join(tempdatapath, filename)
    with open(tempfilepath, 'w', encoding='utf8') as tempfile:
        tempfile.write("test1,test2\ntest3,")
        tempfile.write(size*"a")

    correct = parse_results(filename, "text/csv", result_dict,
                            True, basepath=tmpdir)
    params = {
        "separator": correct.streams[0]["separator"],
        "delimiter": correct.streams[0]["delimiter"],
        "fields": header,
        "mimetype": "text/csv"}
    params.update(extra_params)
    extractor = CsvExtractor(filename=correct.filename, mimetype=MIMETYPE,
                           params=params)
    extractor.extract()

    evaluate_extractor(extractor, correct)


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

    extractor = CsvExtractor(Path(filename), mimetype="text/csv", params=params)
    extractor.extract()
    assert extractor.well_formed
    assert extractor.streams[0].first_line() == \
        ["year", "bränd", "mödel", "detail", "other"]


def test_pdf_as_csv():
    """Test CSV extractor with PDF files."""
    extractor = CsvExtractor(filename=PDF_PATH, mimetype="text/csv")
    extractor.extract()

    assert not extractor.well_formed, extractor.messages() + extractor.errors()
    assert extractor.errors()


@pytest.mark.parametrize(
    "filename",
    [
        ("valid__utf8.csv"),
        ("valid__ascii_header.csv")
    ]
)
def test_no_parameters(filename, evaluate_extractor):
    """
    Test extractor without separate parameters.

    :filename: Test file name
    """
    correct = parse_results(filename, MIMETYPE,
                            {"purpose": "Test valid file on default settings.",
                             "stdout_part": "The file was analyzed",
                             "stderr_part": "",
                             "streams":
                             {0: {"stream_type": "text",
                                  "index": 0,
                                  "mimetype": MIMETYPE,
                                  "version": UNAP,
                                  "delimiter": ",",
                                  "separator": "\r\n",
                                  "quotechar": "\"",
                                  "first_line": ["year", "brand", "model",
                                                 "detail", "other"]}}},
                            True)
    extractor = CsvExtractor(correct.filename, mimetype="text/csv")
    extractor.extract()
    evaluate_extractor(extractor, correct)


def test_bad_parameters():
    """
    Test that CsvMeta raises an error if proper parameters are not given.
    """
    with pytest.raises(ValueError) as err:
        # "separator" is missing from the keys
        CsvMeta(well_formed=True, params={"delimiter": ",", "fields": [],
                                          "first_line": ""})
    assert ("CsvMeta must be given a dict containing keys" in
            str(err.value))


def test_empty_file():
    """
    Test empty file, and that sniffer is not used if delimiter and
    separator are given.

    We first test with empty file that sniffer raises exception if the
    parameters are not given. Secondly, sniffer is skipped when parameters
    are given, but the then extractor raises exception elsewhere.
    """
    extractor = CsvExtractor(Path("tests/data/text_csv/invalid__empty.csv"),
                           mimetype=MIMETYPE)
    extractor.extract()
    assert partial_message_included("Could not determine delimiter",
                                    extractor.errors())
    assert not extractor.well_formed

    extractor = CsvExtractor(Path("tests/data/text_csv/invalid__empty.csv"),
                           mimetype=MIMETYPE,
                           params={"delimiter": ";", "separator": "CRLF"})
    extractor.extract()
    assert partial_message_included("Error reading file as CSV",
                                    extractor.errors())
    assert not extractor.well_formed


def test_nonexistent_file():
    """
    Test that CsvExtractor logs an error when file is not found.
    """
    extractor = CsvExtractor(filename=Path("nonexistent/file.csv"), mimetype="text/csv")
    extractor.extract()
    assert partial_message_included("Error when reading the file: ",
                                    extractor.errors())
    assert not extractor.well_formed


def test_is_supported():
    """
    Test is_supported method.
    """
    mime = MIMETYPE
    ver = ""
    assert CsvExtractor.is_supported(mime, ver, True)
    assert CsvExtractor.is_supported(mime, None, True)
    assert CsvExtractor.is_supported(mime, ver, False)
    assert CsvExtractor.is_supported(mime, "foo", True)
    assert not CsvExtractor.is_supported("foo", ver, True)


def test_tools():
    """
    Test that there are no thirdparty dependencies for csv.
    """
    extractor = CsvExtractor(Path("testfilename"), "test/mimetype")
    assert extractor.tools() == {}
