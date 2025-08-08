"""
Tests for Office extractor.

This module tests that:
    - MIME type, version, streams and well-formedness of well-formed office
      files (odt, doc, docx, odp, ppt, pptx, ods, xsl, xlsx, odg and odf) are
      determined correctly and without anything recorded in extractor errors.
    - MIME type, version, streams and well-formedness of corrupted office
      files are determined correctly with 'source file could not be loaded'
      being recorded in extractpr errors.
    - Extractor uses parallel instances of LibreOffice properly.
    - The following MIME type and version combinations are supported:
        - application/vnd.oasis.opendocument.text, 1.2, 1.3
        - application/msword, 97-2003
        - application/vnd.openxmlformats-officedocument.wordprocessingml.document, 2007 onwards
        - application/vnd.oasis.opendocument.presentation, 1.2, 1.3
        - application/vnd.ms-powerpoint, 97-2003
        - application/vnd.openxmlformats-officedocument.presentationml.presentation, 2007 onwards
        - application/vnd.oasis.opendocument.spreadsheet, 1.2, 1.3
        - application/vnd.ms-excel, 8X
        - application/vnd.openxmlformats-officedocument.spreadsheetml.sheet, 2007 onwards
        - application/vnd.oasis.opendocument.graphics, 1.2, 1.3
        - application/vnd.oasis.opendocument.formula, 1.2, 1.3
    - These MIME types are also supported with a made up version or None as
      the version.
    - A made up MIME type is not supported.
    - Without well-formedness check, none of these MIME types are supported.
"""  # noqa  (it's neater to have long lines than to break mimetypes)

from multiprocessing import Pool
from pathlib import Path

import pytest

from file_scraper.defaults import UNAV
from file_scraper.office.office_extractor import OfficeExtractor
from tests.common import parse_results, partial_message_included

BASEPATH = "tests/data"


@pytest.mark.parametrize(
    ["filename", "mimetype"],
    [
        ("valid_1.2.odt", "application/vnd.oasis.opendocument.text"),
        ("valid_1.3.odt", "application/vnd.oasis.opendocument.text"),
        ("valid_97-2003.doc", "application/msword"),
        ("valid_2007 onwards.docx", "application/vnd.openxmlformats-"
         "officedocument.wordprocessingml.document"),
        ("valid_1.2.odp",
         "application/vnd.oasis.opendocument.presentation"),
        ("valid_1.3.odp",
         "application/vnd.oasis.opendocument.presentation"),
        ("valid_97-2003.ppt", "application/vnd.ms-powerpoint"),
        ("valid_2007 onwards.pptx", "application/vnd.openxml"
         "formats-officedocument.presentationml.presentation"),
        ("valid_1.2.ods",
         "application/vnd.oasis.opendocument.spreadsheet"),
        ("valid_1.3.ods",
         "application/vnd.oasis.opendocument.spreadsheet"),
        ("valid_8X.xls", "application/vnd.ms-excel"),
        ("valid_2007 onwards.xlsx", "application/vnd."
         "openxmlformats-officedocument.spreadsheetml.sheet"),
        ("valid_1.2.odg", "application/vnd.oasis.opendocument.graphics"),
        ("valid_1.3.odg", "application/vnd.oasis.opendocument.graphics"),
        ("valid_1.2.odf", "application/vnd.oasis.opendocument.formula"),
        ("valid_1.3.odf", "application/vnd.oasis.opendocument.formula"),
    ]
)
def test_extractor_valid_file(filename, mimetype, evaluate_extractor):
    """
    Test valid files with extractor.

    :filename: Test file name
    :mimetype: File MIME type
    """
    correct = parse_results(filename, mimetype, {}, True)
    extractor = OfficeExtractor(filename=correct.filename, mimetype=mimetype)
    extractor.scrape_file()
    correct.update_mimetype(UNAV)
    correct.update_version(UNAV)

    evaluate_extractor(extractor, correct, False)
    assert extractor.messages()
    assert not extractor.errors()


@pytest.mark.parametrize(
    ["filename", "mimetype", "application"],
    [
        ("valid_1.2.odt", "application/vnd.oasis.opendocument.text",
         "writer"),
        ("valid_1.3.odt", "application/vnd.oasis.opendocument.text",
         "writer"),
        ("valid_97-2003.doc", "application/msword", "writer"),
        ("valid_2007 onwards.docx",
         "application/vnd.openxmlformats-officedocument.wordprocessingml.document", # noqa
         "writer"),
        ("valid_1.2.odp",
         "application/vnd.oasis.opendocument.presentation", "impress"),
        ("valid_1.3.odp",
         "application/vnd.oasis.opendocument.presentation", "impress"),
        ("valid_97-2003.ppt", "application/vnd.ms-powerpoint", "impress"),
        ("valid_2007 onwards.pptx",
         "application/vnd.openxmlformats-officedocument.presentationml.presentation", # noqa
         "impress"),
        ("valid_1.2.ods",
         "application/vnd.oasis.opendocument.spreadsheet", "calc"),
        ("valid_1.3.ods",
         "application/vnd.oasis.opendocument.spreadsheet", "calc"),
        ("valid_8X.xls", "application/vnd.ms-excel", "calc"),
        ("valid_2007 onwards.xlsx",
         "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
         "calc"),
        ("valid_1.2.odg", "application/vnd.oasis.opendocument.graphics",
         "draw"),
        ("valid_1.3.odg", "application/vnd.oasis.opendocument.graphics",
         "draw"),
        ("valid_1.2.odf", "application/vnd.oasis.opendocument.formula",
         "math"),
        ("valid_1.3.odf", "application/vnd.oasis.opendocument.formula",
         "math"),
    ]
)
def test_extractor_correct_application(filename, mimetype, application):
    """
    Test that the correct LibreOffice application is selected.

    If all necessary LibreOffice components are not installed, some files may
    be scraped with a different application than intended (e.g. using Impress
    for ODG files), and this may work, but it should not be relied on. This
    test makes sure that all components are present and they are used for the
    correct files.

    :filename: Test file name
    :mimetype: File MIME type
    :application: Correct office application
    """
    testfile = Path("tests/data", mimetype.replace("/", "_"),
                    filename)

    extractor = OfficeExtractor(filename=testfile, mimetype=mimetype)
    extractor.scrape_file()

    assert partial_message_included(f"using filter : {application}",
                                    extractor.messages())


@pytest.mark.parametrize(
    ["filename", "mimetype"],
    [
        ("invalid_1.2_corrupted.odt", "application/vnd.oasis.opendocument"
         ".text"),
        ("invalid_1.3_corrupted.odt", "application/vnd.oasis.opendocument"
         ".text"),
        ("invalid_2007 onwards_corrupted.docx", "application/"
         "vnd.openxmlformats-officedocument.wordprocessingml.document"),
        ("invalid_1.2_corrupted.odp",
         "application/vnd.oasis.opendocument.presentation"),
        ("invalid_1.3_corrupted.odp",
         "application/vnd.oasis.opendocument.presentation"),
        ("invalid_2007 onwards_corrupted.pptx", "application/vnd.openxml"
         "formats-officedocument.presentationml.presentation"),
        ("invalid_1.2_corrupted.ods",
         "application/vnd.oasis.opendocument.spreadsheet"),
        ("invalid_1.3_corrupted.ods",
         "application/vnd.oasis.opendocument.spreadsheet"),
        ("invalid_2007 onwards_corrupted.xlsx", "application/vnd."
         "openxmlformats-officedocument.spreadsheetml.sheet"),
        ("invalid_1.2_corrupted.odg", "application/vnd.oasis.opendocument"
         ".graphics"),
        ("invalid_1.3_corrupted.odg", "application/vnd.oasis.opendocument"
         ".graphics"),
        ("invalid_1.2_corrupted.odf", "application/vnd.oasis.opendocument"
         ".formula"),
        ("invalid_1.3_corrupted.odf", "application/vnd.oasis.opendocument"
         ".formula"),
    ]
)
def test_extractor_invalid_file(filename, mimetype, evaluate_extractor):
    """
    Test extractor with invalid files.

    :filename: Test file name
    :mimetype: File MIME type
    """
    result_dict = {
        "purpose": "Test invalid file.",
        "stdout_part": "",
        "stderr_part": "source file could not be loaded"}
    correct = parse_results(filename, mimetype, result_dict, True)
    extractor = OfficeExtractor(filename=correct.filename, mimetype=mimetype)
    extractor.scrape_file()
    correct.streams[0]["version"] = UNAV
    correct.streams[0]["mimetype"] = UNAV

    evaluate_extractor(extractor, correct)


def _scrape(filename, mimetype):
    extractor = OfficeExtractor(
        filename=Path(BASEPATH, mimetype.replace("/", "_"),
                      filename), mimetype=mimetype)
    extractor.scrape_file()
    return extractor.well_formed


@pytest.mark.parametrize(
    ["filename", "mimetype"],
    [
        ("valid_1.2.odt", "application/vnd.oasis.opendocument.text"),
    ]
)
def test_parallel_validation(filename, mimetype):
    """
    Test validation in parallel.

    This is done because Libreoffice convert command is prone for
    freezing which would cause TimeOutError here.

    :filename: Test file name
    :mimetype: File MIME type
    """

    number = 3
    with Pool(number) as pool:
        results = [pool.apply_async(_scrape, (filename, mimetype))
                   for _ in range(number)]

        for result in results:
            assert result.get(timeout=5)


@pytest.mark.usefixtures("patch_shell_attributes_fx")
def test_office_returns_invalid_return_code():
    """Test that a correct error message is given
    when the tool gives an invalid return code"""
    mimetype = "application/vnd.oasis.opendocument.text"
    path = Path("tests/data", mimetype.replace("/", "_"))
    testfile = path / "valid_1.2.odt"

    extractor = OfficeExtractor(filename=testfile,
                              mimetype=mimetype)

    extractor.scrape_file()

    assert "Office returned invalid return code: -1\n" in extractor.errors()


@pytest.mark.parametrize(
    ["mime", "ver"],
    [
        ("application/vnd.oasis.opendocument.text", "1.2"),
        ("application/vnd.oasis.opendocument.text", "1.3"),
        ("application/msword", "97-2003"),
        ("application/vnd.openxmlformats-"
         "officedocument.wordprocessingml.document", "2007 onwards"),
        ("application/vnd.oasis.opendocument.presentation", "1.2"),
        ("application/vnd.oasis.opendocument.presentation", "1.3"),
        ("application/vnd.ms-powerpoint", "97-2003"),
        ("application/vnd.openxml"
         "formats-officedocument.presentationml.presentation", "2007 onwards"),
        ("application/vnd.oasis.opendocument.spreadsheet", "1.2"),
        ("application/vnd.oasis.opendocument.spreadsheet", "1.3"),
        ("application/vnd.ms-excel", "8X"),
        ("application/vnd."
         "openxmlformats-officedocument.spreadsheetml.sheet", "2007 onwards"),
        ("application/vnd.oasis.opendocument.graphics", "1.2"),
        ("application/vnd.oasis.opendocument.graphics", "1.3"),
        ("application/vnd.oasis.opendocument.formula", "1.2"),
        ("application/vnd.oasis.opendocument.formula", "1.3"),
    ]
)
def test_is_supported(mime, ver):
    """
    Test is_supported method.

    :mime: MIME type
    :ver: File format version
    """
    assert OfficeExtractor.is_supported(mime, ver, True)
    assert OfficeExtractor.is_supported(mime, None, True)
    assert not OfficeExtractor.is_supported(mime, ver, False)
    assert OfficeExtractor.is_supported(mime, "foo", True)
    assert not OfficeExtractor.is_supported("foo", ver, True)


def test_tools():
    """Test that tool versions have at least one digit in the start"""
    extractor = OfficeExtractor(filename=Path(""), mimetype="")
    assert extractor.tools()["libreoffice"]["version"][0].isdigit()
