"""
Test module for jhove.py

This module tests that:
    - MIME type, version, streams and well-formedness of gif 1987a and 1989a
      files is tested correctly.
        - For well-formed files, scraper messages contains "Well-Formed and
          valid".
        - For files with broken header, scraper errors contains "Invalid GIF
          header".
        - For truncated files, scraper errors contains "Unknown data block
          type".
        - For empty files, scraper errors contains "Wrong Application Extension
          block size".
    - The scraper can handle output from old versions of JHove. JHove's
      namespaces were updated between versions 1.20 and 1.24, from the old
      Harvard namespace to the new OPF namespace. Scraper should function with
      both versions.
    - MIME type, version, streams and well-formedness of tiff files is tested
      correctly.
        - For well-formed files, scraper messages contains "Well-Formed and
          valid".
        - For files with altered payload, scraper messages contains "IDF offset
          not word-aligned".
        - For files with wrong byte order reported, scraper messages contains
          "No TIFF magic number".
        - For empty files, scraper errors contains "File is too short".
    - MIME type, version, streams and well-formedness of dng files is tested
      correctly.
        - For well-formed files, scraper messages contains "Well-Formed and
          valid".
        - For invalid files with corrupted headers, scraper errors contain
          "Value offset not word-aligned".
        -For empty files, scraper error contains "File is too short".
    - MIME type, version, streams and well-formedness of UTF-8 text files is
      tested correctly.
        - For files with UTF-8 and ASCII (backwards compatibility) encodings
          scraper messages contains "Well-Formed and valid".
        - For files with ISO-8859 encoding scraper errors contains "Not valid
          second byte of UTF-8 encoding"
    - MIME type, version, streams and well-formedness of pdf 1.2, 1.3, 1.4,
      1.5, 1.6 and A-1a files is tested correctly.
        - For valid files, scraper messages contains "Well-formed and valid".
        - For files with altered payload, scraper errors contains "catalog
          dictionary". This is a bit short since the error message is slightly
          differently worded for different versions, but this bit is common for
          all.
        - For files with removed xref entry, scraper errors contains
          "Improperly nested dictionary delimiters".
        - For files with wrong version in header, scraper errors contains
          "MIME type application/pdf with version X is not supported", where X
          is the tested version number.
    - Possible errors with scraping pdf 1.7 files are ignored, as that
      version is not supported JHove. Scraping 1.7 files should not fail,
      since JHove is used for determining the root version for all pdf files.
    - The scraper reports the root version of archive and non-archive pdf
      files.
    - MIME type, version, streams and well-formedness of jpeg 1.01 files is
      tested correctly
        - For valid files, scraper messages contains "Well-formed and valid".
        - For files with altered payload, scraper errors contains "Unexpected
          end of file".
        - For files without FF D8 FF start marker, scraper errors contains
          "Invalid JPEG header".
        - For empty files, scraper errors contains "Invalid JPEG header".
    - MIME type, version, streams and well-formedness of html 4.01 and
      xhtml 1.0 files is tested correctly
        - For valid files, scraper messages contains "Well-formed and valid".
        - For valid html file with version not supported by the scraper,
          scraper errors contains "Unrecognized or missing DOCTYPE
          declaration".
        - For html files with illegal tags, scraper errors contains "Unknown
          tag".
        - For html files without doctype, scraper errors contains
          "Unrecognized or missing DOCTYPE declaration".
        - For empty files, scraper errors contains "Document is empty".
        - For xhtml files with illegal tags, scraper errors contains "must be
          declared".
        - For xhtml files without doctype, scraper errors contains "Cannot
          find the declaration of element".
    - MIME type, version, streams and well-formedness of bwf and wav files is
      tested correctly
        - For valid files, scraper messages contains "Well-formed and valid".
        - For bwf files with missing bytes, scraper messages contains "Chunk ID
          character outside printable ASCII range".
        - For bwf and wav files with bytes removed from the RIFF tag, scraper
          errors contains "Invalid chunk size".
        - For empty files, scraper errors contains "Unexpected end of file".
        - For files with missing data bytes, scraper errors contains "Bytes
          missing".
    - MIME type, version, streams and well-formedness of aiff and aiff-c
      files is tested correctly
        - For valid files, scraper messages contains "Well-formed and valid".
    - The following MIME-type and version pairs are supported by their
      respective scrapers when well-formedness is checked, in addition to
      which these MIME types are also supported with None or a made up version.
      When well-formedness is not checked, these MIME types are not supported.
        - image/gif, 1989a
        - image/tiff, 6.0
        - image/jpeg, 1.01
        - audio/x-wav, 2
    - The following MIME type and version pairs are supported by their
      respective scrapers when well-formedness is checked. They are not
      supported with a made up version or when well-formedness is not checked.
        - application/pdf, 1.4
        - text/html, 4.01
        - application/xhtml+xml, 1.0
    - Utf8JHove reports MIME type text/plain with "", None or a made up version
      as not supported, as well as a made up MIME type.
    - JHove scarper works as designed when charset parameter for (X)HTML files
      is given
    - MIME type, version, streams and well-formedness of EPUB files is tested
      correctly
        - For valid files, scraper messages contains "Well-formed and valid".
        - For EPUB files where mimetype is not located first in the package,
          scraper errors contains "Mimetype file entry is missing".
        - For EPUB 3 files created with LibreOffice's built-in export function,
          scraper errors contains "The 'head' element should have a 'title'
          child element".
        - For EPUB 2 files created with LibreOffice's built-in export function,
          scraper errors contains "element \"title\" not allowed here".
"""
import os

import pytest

from file_scraper.shell import Shell
from file_scraper.defaults import UNAV
from file_scraper.jhove.jhove_scraper import (JHoveAiffScraper,
                                              JHoveDngScraper,
                                              JHoveEpubScraper,
                                              JHoveGifScraper,
                                              JHoveHtmlScraper,
                                              JHoveJpegScraper,
                                              JHovePdfScraper,
                                              JHoveTiffScraper,
                                              JHoveUtf8Scraper,
                                              JHoveWavScraper)
from tests.common import (parse_results, partial_message_included)


@pytest.mark.parametrize(
    ["filename", "result_dict"],
    [
        ("valid_XXXXa.gif", {
            "purpose": "Test valid file.",
            "stdout_part": "Well-Formed and valid",
            "stderr_part": ""}),
        ("invalid_XXXXa_broken_header.gif", {
            "purpose": "Test invalid header.",
            "stdout_part": "",
            "stderr_part": "Invalid GIF header"}),
        ("invalid_XXXXa_truncated.gif", {
            "purpose": "Test truncated file.",
            "stdout_part": "",
            "stderr_part": "Unknown data block type"}),
        ("invalid__empty.gif", {
            "purpose": "Test empty file.",
            "stdout_part": "",
            "stderr_part": "Wrong Application Extension block size"})
    ]
)
def test_scraper_gif(filename, result_dict, evaluate_scraper):
    """
    Test gif scraping.

    :filename: Test file name
    :result_dict: Result dict containing test purpose, and parts of
                  expected results of stdout and stderr
    """
    for version in ["1987", "1989"]:
        current_filename = filename.replace("XXXX", version)
        correct = parse_results(current_filename, "image/gif",
                                result_dict, True)
        correct.update_mimetype("image/gif")
        scraper = JHoveGifScraper(filename=correct.filename,
                                  mimetype="image/gif")
        scraper.scrape_file()

        evaluate_scraper(scraper, correct)


@pytest.mark.parametrize(
    ["filename", "result_dict"],
    [
        ("valid_XXXXa.gif", {
            "purpose": "Test valid file.",
            "stdout_part": "Well-Formed and valid",
            "stderr_part": ""}),
        ("invalid_XXXXa_broken_header.gif", {
            "purpose": "Test invalid header.",
            "stdout_part": "",
            "stderr_part": "Invalid GIF header"}),
        ("invalid_XXXXa_truncated.gif", {
            "purpose": "Test truncated file.",
            "stdout_part": "",
            "stderr_part": "Unknown data block type"}),
        ("invalid__empty.gif", {
            "purpose": "Test empty file.",
            "stdout_part": "",
            "stderr_part": "Wrong Application Extension block size"})
    ]
)
def test_old_namespace(filename, result_dict, evaluate_scraper, monkeypatch):
    """
    Test that scraper works as expected even if it were to be run with old
    version of JHove. I.e. if the namespace is the old Harvard variant.

    Mocks the results of Shell stdout to edit the XML output.
    """

    @property
    def _mock_stdout_raw(self):
        """
        Standard output from command.
        Replace new OPF namespace with old Harvard one.
        """
        mock_output = self.popen()["stdout"]

        if self.command[0:4] == ["jhove", "-h", "XML", "-m"]:
            assert (b"http://schema.openpreservation.org/ois/xml/ns/jhove" in
                    mock_output)
            mock_output = mock_output.replace(
                    b"http://schema.openpreservation.org/ois/xml/ns/jhove",
                    b"http://hul.harvard.edu/ois/xml/ns/jhove")
            mock_output = mock_output.replace(
                    b"https://schema.openpreservation.org/ois/xml/xsd/jhove/"
                    b"1.8/jhove.xsd",
                    b"http://hul.harvard.edu/ois/xml/xsd/jhove/1.6/jhove.xsd")
        return mock_output

    monkeypatch.setattr(Shell, "stdout_raw", _mock_stdout_raw)
    for version in ["1987", "1989"]:
        current_filename = filename.replace("XXXX", version)
        correct = parse_results(current_filename, "image/gif",
                                result_dict, True)
        correct.update_mimetype("image/gif")
        scraper = JHoveGifScraper(filename=correct.filename,
                                  mimetype="image/gif")
        scraper.scrape_file()
        assert "hul.harvard.edu" in scraper._report.values()[0]

        evaluate_scraper(scraper, correct)


@pytest.mark.parametrize(
    ["filename", "result_dict"],
    [
        ("valid_6.0.tif", {
            "purpose": "Test valid file.",
            "stdout_part": "Well-Formed and valid",
            "stderr_part": ""}),
        ("invalid_6.0_payload_altered.tif", {
            "purpose": "Test payload altered in file.",
            "stdout_part": "",
            "stderr_part": "IFD offset not word-aligned"}),
        ("invalid_6.0_wrong_byte_order.tif", {
            "purpose": "Test wrong byte order in file.",
            "stdout_part": "",
            "stderr_part": "No TIFF magic number"}),
        ("invalid__empty.tif", {
            "purpose": "Test empty file.",
            "stdout_part": "",
            "stderr_part": "File is too short"}),
    ]
)
def test_scraper_tiff(filename, result_dict, evaluate_scraper):
    """
    Test tiff scraping.

    :filename: Test file name
    :result_dict: Result dict containing test purpose, and parts of
                  expected results of stdout and stderr
    """
    correct = parse_results(filename, "image/tiff",
                            result_dict, True)
    correct.update_mimetype("image/tiff")
    scraper = JHoveTiffScraper(filename=correct.filename,
                               mimetype="image/tiff")
    scraper.scrape_file()

    evaluate_scraper(scraper, correct)


@pytest.mark.parametrize(
    ["filename", "result_dict"],
    [
        ("valid_1.4.dng", {
            "purpose": "Test valid file.",
            "stdout_part": "Well-Formed and valid",
            "stderr_part": ""}),
        ("invalid_1.4_edited_header.dng", {
            "purpose": "Test invalid file with edited header.",
            "stdout_part": "",
            "stderr_part": "Value offset not word-aligned"}),
        ("invalid__empty.dng", {
            "purpose": "Test empty file",
            "stdout_part": "",
            "stderr_part": "File is too short"})
    ]
)
def test_scraper_dng(filename, result_dict, evaluate_scraper):
    """
    Test dng scraping.

    :filename: Test file name
    :result_dict: Result dict containing test purpose, and parts of expected
                  results of streams, stdout and stderr
    """
    correct = parse_results(filename, "image/x-adobe-dng", result_dict, True)
    correct.update_mimetype("image/x-adobe-dng")
    correct.update_version(UNAV)
    scraper = JHoveDngScraper(filename=correct.filename,
                              mimetype="image/x-adobe-dng")
    scraper.scrape_file()

    evaluate_scraper(scraper, correct)


@pytest.mark.parametrize(
    ["filename", "result_dict"],
    [
        ("valid__utf8_without_bom.txt", {
            "purpose": "Test valid UTF-8 file.",
            "stdout_part": "Well-Formed and valid",
            "stderr_part": ""}),
        ("valid__ascii.txt", {
            "purpose": "Test valid ASCII file.",
            "stdout_part": "Well-Formed and valid",
            "stderr_part": ""}),
        ("valid__iso8859.txt", {
            "purpose": "Test valid ISO-8859 file, which is invalid.",
            "inverse": True,
            "stdout_part": "",
            "stderr_part": "Not valid second byte of UTF-8 encoding"})
    ]
)
def test_scraper_utf8(filename, result_dict, evaluate_scraper):
    """
    Test utf8 text file scraping.

    :filename: Test file name
    :result_dict: Result dict containing test purpose, parts of
                  expected results of stdout and stderr, and inverse
                  well-formed result
    """
    correct = parse_results(filename, "text/plain", result_dict, True,
                            {"charset": "UTF-8"})
    scraper = JHoveUtf8Scraper(filename=correct.filename,
                               mimetype="text/plain",
                               params=correct.params)
    scraper.scrape_file()
    correct.streams[0]["mimetype"] = UNAV
    correct.streams[0]["version"] = UNAV

    evaluate_scraper(scraper, correct)


@pytest.mark.parametrize(
    ["filename", "result_dict"],
    [
        ("valid_X.pdf", {
            "purpose": "Test valid file.",
            "stdout_part": "Well-Formed and valid",
            "stderr_part": ""}),
    ]
)
def test_scraper_pdf_valid(filename, result_dict, evaluate_scraper):
    """
    Test pdf scraping for valid files.

    JHove detects the root version of PDF/A files in its `version` field, but
    `parse_results` gets the expected version from the filename. Thus the
    correct version has to be updated for the test to work correctly for
    version A-1a.

    :filename: Test file name
    :result_dict: Result dict containing test purpose, and parts of
                  expected results of stdout and stderr
    """
    for ver in ["1.2", "1.3", "1.4", "1.5", "1.6", "A-1a"]:
        current_filename = filename.replace("X", ver)
        correct = parse_results(current_filename, "application/pdf",
                                result_dict, True)
        correct.update_mimetype("application/pdf")
        if ver == "A-1a":
            correct.update_version("1.4")
        scraper = JHovePdfScraper(filename=correct.filename,
                                  mimetype="application/pdf")
        scraper.scrape_file()

        evaluate_scraper(scraper, correct)


@pytest.mark.parametrize(
    ["filename", "result_dict"],
    [
        ("invalid_X_payload_altered.pdf", {
            "purpose": "Test payload altered file.",
            "stdout_part": "",
            "stderr_part": "catalog dictionary"}),
        ("invalid_X_removed_xref.pdf", {
            "purpose": "Test xref change.",
            "stdout_part": "",
            "stderr_part": "Improperly nested dictionary delimiters"}),
    ]
)
def test_scraper_pdf_invalid(filename, result_dict, evaluate_scraper):
    """
    Test pdf scraping for invalid files.

    :filename: Test file name
    :result_dict: Result dict containing test purpose, and parts of
                  expected results of stdout and stderr
    """
    for ver in ["1.2", "1.3", "1.4", "1.5", "1.6", "A-1a"]:
        current_filename = filename.replace("X", ver)
        correct = parse_results(current_filename, "application/pdf",
                                result_dict, True)
        correct.update_mimetype("application/pdf")
        scraper = JHovePdfScraper(filename=correct.filename,
                                  mimetype="application/pdf")
        scraper.scrape_file()

        evaluate_scraper(scraper, correct)


@pytest.mark.parametrize(
    ["filename", "version"],
    [
        ["tests/data/application_pdf/valid_1.4.pdf", "1.4"],
        ["tests/data/application_pdf/valid_A-1a_root_1.6.pdf", "1.6"],
        ["tests/data/application_pdf/valid_A-1a_root_1.7.pdf", "1.7"],
        ["tests/data/application_pdf/valid_A-1b_root_1.7.pdf", "1.7"],
        ["tests/data/application_pdf/valid_A-2u_root_1.5.pdf", "1.5"]
    ]
)
def test_pdf_root_version_in_results(filename, version):
    """
    Test that the root version of a PDF is reported in messages.
    """
    scraper = JHovePdfScraper(
        filename=filename,
        mimetype="application/pdf")
    scraper.scrape_file()
    assert f"PDF root version is {version}" in scraper.messages()


def test_pdf_17_scraping_result_ignored():
    """
    Test that JHovePdfScraper ignores pdf 1.7 scraping results.

    JHove does not support PDF version 1.7, but before running the scrapers, we
    don't know what the exact version is. Thus, in case we encounter a PDF 1.7,
    we must ignore the error messages normally produced by JHove and instead
    log a message letting the user know that the scraping result from JHove was
    ignored.
    """
    scraper = JHovePdfScraper(
        filename="tests/data/application_pdf/valid_1.7.pdf",
        mimetype="application/pdf")
    scraper.scrape_file()
    assert not scraper.errors()
    assert ("JHove does not support PDF 1.7: All errors and messages ignored."
            in scraper.messages())


@pytest.mark.parametrize(
    ["version_in_filename", "found_version"],
    [
        ["1.2", "1.0"],
        ["1.3", "1.0"],
        ["1.5", "1.1"],
        ["1.6", "1.1"],
        ["A-1a", "1.0"],
    ])
def test_scraper_invalid_pdfversion(version_in_filename, found_version):
    """
    Test that unsupported version is detected.
    """
    scraper = JHovePdfScraper(
        filename="tests/data/application_pdf/invalid_X_wrong_version"
                 ".pdf".replace("X", version_in_filename),
        mimetype="application/pdf")
    scraper.scrape_file()
    assert partial_message_included(
        "MIME type application/pdf with version {} is not "
        "supported.".format(found_version), scraper.errors())
    assert not scraper.well_formed


@pytest.mark.parametrize(
    ["filename", "result_dict"],
    [
        ("valid_1.01.jpg", {
            "purpose": "Test valid file.",
            "stdout_part": "Well-Formed and valid",
            "stderr_part": ""}),
        ("invalid_1.01_data_changed.jpg", {
            "purpose": "Test image data change in file.",
            "stdout_part": "",
            "stderr_part": "Unexpected end of file"}),
        ("invalid_1.01_no_start_marker.jpg", {
            "purpose": "Test start marker change in file.",
            "stdout_part": "",
            "stderr_part": "Invalid JPEG header"}),
        ("invalid__empty.jpg", {
            "purpose": "Test empty file.",
            "stdout_part": "",
            "stderr_part": "Invalid JPEG header"})
    ]
)
def test_scraper_jpeg(filename, result_dict, evaluate_scraper):
    """
    Test jpeg scraping.

    :filename: Test file name
    :result_dict: Result dict containing test purpose, and parts of
                  expected results of stdout and stderr
    """
    correct = parse_results(filename, "image/jpeg",
                            result_dict, True)
    correct.update_mimetype("image/jpeg")
    scraper = JHoveJpegScraper(filename=correct.filename,
                               mimetype="image/jpeg")
    scraper.scrape_file()
    correct.streams[0]["version"] = UNAV

    evaluate_scraper(scraper, correct)


# pylint: disable=too-many-arguments
@pytest.mark.parametrize(
    ["filename", "result_dict", "mimetype", "charset"],
    [
        ("valid_4.01.html", {
            "purpose": "Test valid file with correctly specified charset.",
            "stdout_part": "Well-Formed and valid",
            "stderr_part": ""},
         "text/html", "UTF-8"),
        ("valid_4.01.html", {
            "purpose": "Test valid file with incorrectly specified charset.",
            "stdout_part": "",
            "inverse": True,
            "stderr_part": "Found encoding declaration UTF-8"},
         "text/html", "ISO-8859-15"),
        ("valid_1.0.xhtml", {
            "purpose": "Test valid file.",
            "stdout_part": "Well-Formed and valid",
            "stderr_part": ""},
         "application/xhtml+xml", "UTF-8"),
        ("valid_5.html", {
            "purpose": "Test valid file, which is invalid for this scraper.",
            "inverse": True,
            "stdout_part": "",
            "stderr_part": "Unrecognized or missing DOCTYPE declaration"},
         "text/html", "UTF-8"),
        ("invalid_4.01_illegal_tags.html", {
            "purpose": "Test illegal tag.",
            "stdout_part": "",
            "stderr_part": "Unknown tag"},
         "text/html", "UTF-8"),
        ("invalid_4.01_nodoctype.html", {
            "purpose": "Test without doctype.",
            "stdout_part": "",
            "stderr_part": "Unrecognized or missing DOCTYPE declaration"},
         "text/html", "UTF-8"),
        ("invalid__empty.html", {
            "purpose": "Test empty file.",
            "stdout_part": "",
            "stderr_part": "Document is empty"},
         "text/html", "UTF-8"),
        ("invalid_1.0_illegal_tags.xhtml", {
            "purpose": "Test illegal tag.",
            "stdout_part": "",
            "stderr_part": "must be declared."},
         "application/xhtml+xml", "UTF-8"),
        ("invalid_1.0_missing_closing_tag.xhtml", {
            "purpose": "Test missing closing tag.",
            "stdout_part": "",
            "stderr_part": "must be terminated by the matching end-tag"},
         "application/xhtml+xml", "UTF-8"),
        ("invalid_1.0_no_doctype.xhtml", {
            "purpose": "Test without doctype.",
            "stdout_part": "",
            "stderr_part": "Cannot find the declaration of element"},
         "application/xhtml+xml", "UTF-8"),
        ("invalid__empty.xhtml", {
            "purpose": "Test empty file.",
            "stdout_part": "",
            "stderr_part": "Document is empty"},
         "application/xhtml+xml", "UTF-8")
    ]
)
def test_scraper_html(filename, result_dict, mimetype, charset,
                      evaluate_scraper):
    """
    Test html and xhtml scraping.

    :filename: Test file name
    :result_dict: Result dict containing test purpose, and parts of
                  expected results of stdout and stderr
    :mimetype: File MIME type
    :charset: File character encoding
    """
    params = {"charset": charset}
    correct = parse_results(filename, mimetype, result_dict, True,
                            params)
    if not correct.well_formed:
        correct.streams[0]["stream_type"] = UNAV
    else:
        correct.streams[0]["stream_type"] = "text"

    if filename == "valid_4.01.html":
        correct.update_mimetype("text/html")
        correct.update_version("4.01")
        correct.streams[0]["charset"] = "UTF-8"
        correct.streams[0]["stream_type"] = "text"

    scraper = JHoveHtmlScraper(filename=correct.filename,
                               mimetype=mimetype,
                               params=correct.params)
    scraper.scrape_file()

    evaluate_scraper(scraper, correct)


@pytest.mark.parametrize(
    ["filename", "result_dict"],
    [
        ("valid__wav.wav", {
            "purpose": "Test valid file.",
            "stdout_part": "Well-Formed and valid",
            "stderr_part": ""}),
        ("valid_2_bwf.wav", {
            "purpose": "Test valid file.",
            "stdout_part": "Well-Formed and valid",
            "stderr_part": ""}),
        ("invalid_2_bwf_data_bytes_missing.wav", {
            "purpose": "Test data bytes missing.",
            "stdout_part": "",
            "stderr_part": "Chunk ID character outside printable "
                           "ASCII range"}),
        ("invalid_2_bwf_RIFF_edited.wav", {
            "purpose": "Test edited RIFF.",
            "stdout_part": "",
            "stderr_part": "Invalid chunk size"}),
        ("invalid__data_bytes_missing.wav", {
            "purpose": "Test data bytes missing.",
            "stdout_part": "",
            "stderr_part": "Bytes missing"}),
        ("invalid__RIFF_edited.wav", {
            "purpose": "Test edited RIFF.",
            "stdout_part": "",
            "stderr_part": "Invalid chunk size"})
    ]
)
def test_scraper_wav(filename, result_dict, evaluate_scraper):
    """
    Test wav and bwf scraping.

    :filename: Test file name
    :result_dict: Result dict containing test purpose, and parts of
                  expected results of stdout and stderr
    """
    correct = parse_results(filename, "audio/x-wav",
                            result_dict, True)
    correct.update_mimetype("audio/x-wav")
    scraper = JHoveWavScraper(filename=correct.filename,
                              mimetype="audio/x-wav")
    scraper.scrape_file()

    evaluate_scraper(scraper, correct)


@pytest.mark.parametrize(
    ["filename", "result_dict"],
    [
        ("valid_1.3.aiff", {
            "purpose": "Test valid AIFF file.",
            "stdout_part": "Well-Formed and valid",
            "stderr_part": ""}),
        ("valid__aiff-c.aiff", {
            "purpose": "Test valid AIFF-C file.",
            "stdout_part": "Well-Formed and valid",
            "stderr_part": ""})
    ]
)
def test_scraper_aiff(filename, result_dict, evaluate_scraper):
    """
    Test AIFF and AIFF-C scraping.

    :filename: Test file name
    :result_dict: Result dict containing test purpose, and parts of
                  expected results of stdout and stderr
    """
    correct = parse_results(filename, "audio/x-aiff",
                            result_dict, True)
    correct.update_mimetype("audio/x-aiff")
    if "1.3" in filename:
        correct.update_version("1.3")
    scraper = JHoveAiffScraper(filename=correct.filename,
                               mimetype="audio/x-aiff")
    scraper.scrape_file()

    evaluate_scraper(scraper, correct)


@pytest.mark.parametrize(
    ["mime", "ver", "class_"],
    [
        ("image/gif", "1989a", JHoveGifScraper),
        ("image/tiff", "6.0", JHoveTiffScraper),
        ("image/jpeg", "1.01", JHoveJpegScraper),
        ("audio/x-wav", "2", JHoveWavScraper)
    ]
)
def test_is_supported_allow(mime, ver, class_):
    """
    Test is_supported method, allow all versions.

    :mime: MIME type
    :ver: File format version
    :class_: Scraper class to test
    """
    assert class_.is_supported(mime, ver, True)
    assert class_.is_supported(mime, None, True)
    assert not class_.is_supported(mime, ver, False)
    assert class_.is_supported(mime, "foo", True)
    assert not class_.is_supported("foo", ver, True)


@pytest.mark.parametrize(
    ["mime", "ver", "class_"],
    [
        ("application/pdf", "1.4", JHovePdfScraper),
        ("text/html", "4.01", JHoveHtmlScraper),
        ("application/xhtml+xml", "1.0", JHoveHtmlScraper),
    ]
)
def test_is_supported_deny(mime, ver, class_):
    """
    Test is_supported method, allow only known versions.

    :mime: MIME type
    :ver: File format version
    :class_: Scraper class to test
    """
    assert class_.is_supported(mime, ver, True)
    assert class_.is_supported(mime, None, True)
    assert not class_.is_supported(mime, ver, False)
    assert not class_.is_supported(mime, "foo", True)
    assert not class_.is_supported("foo", ver, True)


@pytest.mark.parametrize(
    ["mime", "ver", "class_"],
    [
        ("text/plain", "", JHoveUtf8Scraper)
    ]
)
def test_is_supported_utf8(mime, ver, class_):
    """
    Test is_supported method, utf8 scraper.

    :mime: MIME type
    :ver: File format version
    :class_: Scraper class to test
    """
    assert not class_.is_supported(mime, ver, True)
    assert not class_.is_supported(mime, None, True)
    assert not class_.is_supported(mime, ver, False)
    assert not class_.is_supported(mime, "foo", True)
    assert not class_.is_supported("foo", ver, True)


@pytest.mark.parametrize(
    ["filename", "mimetype", "charset", "well_formed"],
    [
        ("tests/data/application_xhtml+xml/valid_1.0.xhtml",
         "application/xhtml+xml", "UTF-8", True),
        ("tests/data/application_xhtml+xml/valid_1.0.xhtml",
         "application/xhtml+xml", "ISO-8859-15", False),
        ("tests/data/text_html/valid_4.01.html", "text/html", "UTF-8", True),
        ("tests/data/text_html/valid_4.01.html", "text/html", "ISO-8859-15",
         False),
        ("tests/data/text_html/valid_4.01.html", "text/html", None, False),
    ]
)
def test_charset(filename, mimetype, charset, well_formed):
    """
    Test charset parameter in JhoveHtmlScraper.

    :filename: Test file path
    :mimetype: File MIME type
    :chraset: File character encoding
    :well_formed: Expected well-formed result
    """
    params = {"charset": charset}
    scraper = JHoveHtmlScraper(filename=filename, mimetype=mimetype,
                               params=params)
    scraper.scrape_file()
    assert scraper.well_formed == well_formed
    if charset:
        if well_formed:
            assert not scraper.errors()
        else:
            assert partial_message_included(
                "Found encoding declaration", scraper.errors())
    else:
        assert partial_message_included("encoding not defined",
                                        scraper.errors())


@pytest.mark.parametrize(
    ["filename", "result_dict"],
    [
        ("valid_3_pages.epub", {
            "purpose": "Test valid file.",
            "stdout_part": "Well-Formed and valid",
            "stderr_part": ""}),
        ("valid_3_calibre.epub", {
            "purpose": "Test valid file made with calibre.",
            "stdout_part": "Well-Formed and valid",
            "stderr_part": ""}),
        ("valid_2.0.1_calibre.epub", {
            "purpose": "Test valid file made with calibre.",
            "stdout_part": "Well-Formed and valid",
            "stderr_part": ""}),
        ("valid_3_libreoffice_writer2epub.epub", {
            "purpose": "Test valid file made with libreoffice extension.",
            "stdout_part": "Well-Formed and valid",
            "stderr_part": ""}),
        ("invalid_3_mimetype_not_first.epub", {
            "purpose": "Test invalid epub where mimetype is not first.",
            "stdout_part": "",
            "stderr_part": "Mimetype file entry is missing"}),
        ("invalid_3_libreoffice.epub", {
            "purpose": "Test invalid epub made by LibreOffice export.",
            "stdout_part": "",
            "stderr_part": "The \"head\" element should have a \"title\" "
                           "child element"}),
        ("invalid_2.0.1_libreoffice.epub", {
            "purpose": "Test invalid epub made by LibreOffice export.",
            "stdout_part": "",
            "stderr_part": "element \"title\" not allowed here"}),
    ]
)
def test_scraper_epub(filename, result_dict, evaluate_scraper):
    """
    Test EPUB scraping.

    :filename: Test file name
    :result_dict: Result dict containing test purpose, and parts of
                  expected results of stdout and stderr
    """
    correct = parse_results(filename, "application/epub+zip",
                            result_dict, True)
    correct.update_mimetype("application/epub+zip")
    scraper = JHoveEpubScraper(filename=correct.filename,
                               mimetype="application/epub+zip")
    scraper.scrape_file()

    evaluate_scraper(scraper, correct)


@pytest.mark.usefixtures("patch_shell_attributes_fx")
def test_jhove_returns_invalid_return_code():
    """Test that a correct error message is given
    when the tool gives an invalid return code"""
    mimetype = "application/pdf"
    path = os.path.join("tests/data", mimetype.replace("/", "_"))
    testfile = os.path.join(path, "valid_1.2.pdf")

    scraper = JHovePdfScraper(filename=testfile,
                              mimetype=mimetype)

    scraper.scrape_file()

    assert "JHove returned invalid return code: -1\n" in scraper.errors()


def test_jhove_tools():
    """Test scraper tools return correctly something non nullable"""
    scraper = JHovePdfScraper(filename="",
                              mimetype="")
    assert scraper.tools()["JHOVE"]["version"][0].isdigit()
