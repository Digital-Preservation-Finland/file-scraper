"""
Test module for jhove.py

This module tests that:
    - MIME type, version, streams and well-formedness of gif 1987a and 1989a
      files is tested correctly.
        - For well-formed files, extractor messages contains "Well-Formed and
          valid".
        - For files with broken header, extractor errors contains "Invalid GIF
          header".
        - For truncated files, extractor errors contains "Unknown data block
          type".
        - For empty files, extractor errors contains "Wrong Application Extension
          block size".
    - The extractor can handle output from old versions of JHove. JHove's
      namespaces were updated between versions 1.20 and 1.24, from the old
      Harvard namespace to the new OPF namespace. Extractor should function with
      both versions.
    - MIME type, version, streams and well-formedness of tiff files is tested
      correctly.
        - For well-formed files, extractor messages contains "Well-Formed and
          valid".
        - For files with altered payload, extractor messages contains "IDF offset
          not word-aligned".
        - For files with wrong byte order reported, extractor messages contains
          "No TIFF magic number".
        - For empty files, extractor errors contains "File is too short".
    - MIME type, version, streams and well-formedness of dng files is tested
      correctly.
        - For well-formed files, extractor messages contains "Well-Formed and
          valid".
        - For invalid files with corrupted headers, extractor errors contain
          "Value offset not word-aligned".
        -For empty files, extractor error contains "File is too short".
    - MIME type, version, streams and well-formedness of UTF-8 text files is
      tested correctly.
        - For files with UTF-8 and ASCII (backwards compatibility) encodings
          extractor messages contains "Well-Formed and valid".
        - For files with ISO-8859 encoding extractor errors contains "Not valid
          second byte of UTF-8 encoding"
    - MIME type, version, streams and well-formedness of pdf 1.2, 1.3, 1.4,
      1.5, 1.6 and A-1a files is tested correctly.
        - For valid files, extractor messages contains "Well-formed and valid".
        - For files with altered payload, extractor errors contains "catalog
          dictionary". This is a bit short since the error message is slightly
          differently worded for different versions, but this bit is common for
          all.
        - For files with removed xref entry, extractor errors contains
          "Improperly nested dictionary delimiters".
        - For files with wrong version in header, extractor errors contains
          "MIME type application/pdf with version X is not supported", where X
          is the tested version number.
    - Possible errors with scraping pdf 1.7 files are ignored, as that
      version is not supported JHove. Scraping 1.7 files should not fail,
      since JHove is used for determining the root version for all pdf files.
    - The extractor reports the root version of archive and non-archive pdf
      files.
    - MIME type, version, streams and well-formedness of jpeg 1.01 files is
      tested correctly
        - For valid files, extractor messages contains "Well-formed and valid".
        - For files with altered payload, extractor errors contains "Unexpected
          end of file".
        - For files without FF D8 FF start marker, extractor errors contains
          "Invalid JPEG header".
        - For empty files, extractor errors contains "Invalid JPEG header".
    - MIME type, version, streams and well-formedness of html 4.01 and
      xhtml 1.0 files is tested correctly
        - For valid files, extractor messages contains "Well-formed and valid".
        - For valid html file with version not supported by the extractor,
          extractor errors contains "Unrecognized or missing DOCTYPE
          declaration".
        - For html files with illegal tags, extractor errors contains "Unknown
          tag".
        - For html files without doctype, extractor errors contains
          "Unrecognized or missing DOCTYPE declaration".
        - For empty files, extractor errors contains "Document is empty".
        - For xhtml files with illegal tags, extractor errors contains "must be
          declared".
        - For xhtml files without doctype, extractor errors contains "Cannot
          find the declaration of element".
    - MIME type, version, streams and well-formedness of bwf and wav files is
      tested correctly
        - For valid files, extractor messages contains "Well-formed and valid".
        - For bwf files with missing bytes, extractor messages contains "Chunk ID
          character outside printable ASCII range".
        - For bwf and wav files with bytes removed from the RIFF tag, extractor
          errors contains "Invalid chunk size".
        - For empty files, extractor errors contains "Unexpected end of file".
        - For files with missing data bytes, extractor errors contains "Bytes
          missing".
    - MIME type, version, streams and well-formedness of aiff and aiff-c
      files is tested correctly
        - For valid files, extractor messages contains "Well-formed and valid".
    - The following MIME-type and version pairs are supported by their
      respective extractors when well-formedness is checked, in addition to
      which these MIME types are also supported with None or a made up version.
      When well-formedness is not checked, these MIME types are not supported.
        - image/gif, 1989a
        - image/tiff, 6.0
        - image/jpeg, 1.01
        - audio/x-wav, 2
    - The following MIME type and version pairs are supported by their
      respective extractors when well-formedness is checked. They are not
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
        - For valid files, extractor messages contains "Well-formed and valid".
        - For EPUB files where mimetype is not located first in the package,
          extractor errors contains "Mimetype file entry is missing".
        - For EPUB 3 files created with LibreOffice's built-in export function,
          extractor errors contains "The 'head' element should have a 'title'
          child element".
        - For EPUB 2 files created with LibreOffice's built-in export function,
          extractor errors contains "element \"title\" not allowed here".
"""
from pathlib import Path

import pytest

from file_scraper.shell import Shell
from file_scraper.defaults import UNAV
from file_scraper.paths import resolve_command
from file_scraper.jhove.jhove_extractor import (JHoveAiffExtractor,
                                                JHoveDngExtractor,
                                                JHoveEpubExtractor,
                                                JHoveGifExtractor,
                                                JHoveHtmlExtractor,
                                                JHoveJpegExtractor,
                                                JHovePdfExtractor,
                                                JHoveTiffExtractor,
                                                JHoveUtf8Extractor,
                                                JHoveWavExtractor)
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
def test_extractor_gif(filename, result_dict, evaluate_extractor):
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
        extractor = JHoveGifExtractor(filename=correct.filename,
                                    mimetype="image/gif")
        extractor.extract()

        evaluate_extractor(extractor, correct)


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
def test_old_namespace(filename, result_dict, evaluate_extractor, monkeypatch):
    """
    Test that extractor works as expected even if it were to be run with old
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
        # Shell uses resolve_command so to mock Shell output realistically
        # Need to use the resolve_command function here.
        if self.command[0:4] == [resolve_command("jhove"), "-h", "XML", "-m"]:
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
        extractor = JHoveGifExtractor(filename=correct.filename,
                                    mimetype="image/gif")
        extractor.extract()
        assert "hul.harvard.edu" in extractor._report.values()[0]

        evaluate_extractor(extractor, correct)


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
def test_extractor_tiff(filename, result_dict, evaluate_extractor):
    """
    Test tiff scraping.

    :filename: Test file name
    :result_dict: Result dict containing test purpose, and parts of
                  expected results of stdout and stderr
    """
    correct = parse_results(filename, "image/tiff",
                            result_dict, True)
    correct.update_mimetype("image/tiff")
    extractor = JHoveTiffExtractor(filename=correct.filename,
                                 mimetype="image/tiff")
    extractor.extract()

    evaluate_extractor(extractor, correct)


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
def test_extractor_dng(filename, result_dict, evaluate_extractor):
    """
    Test dng scraping.

    :filename: Test file name
    :result_dict: Result dict containing test purpose, and parts of expected
                  results of streams, stdout and stderr
    """
    correct = parse_results(filename, "image/x-adobe-dng", result_dict, True)
    correct.update_mimetype("image/x-adobe-dng")
    correct.update_version(UNAV)
    extractor = JHoveDngExtractor(filename=correct.filename,
                                mimetype="image/x-adobe-dng")
    extractor.extract()

    evaluate_extractor(extractor, correct)


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
def test_extractor_utf8(filename, result_dict, evaluate_extractor):
    """
    Test utf8 text file scraping.

    :filename: Test file name
    :result_dict: Result dict containing test purpose, parts of
                  expected results of stdout and stderr, and inverse
                  well-formed result
    """
    correct = parse_results(filename, "text/plain", result_dict, True,
                            {"charset": "UTF-8"})
    extractor = JHoveUtf8Extractor(filename=correct.filename,
                                 mimetype="text/plain",
                                 params=correct.params)
    extractor.extract()
    correct.streams[0]["mimetype"] = UNAV
    correct.streams[0]["version"] = UNAV

    evaluate_extractor(extractor, correct)


@pytest.mark.parametrize(
    ["filename", "result_dict"],
    [
        ("valid_X.pdf", {
            "purpose": "Test valid file.",
            "stdout_part": "Well-Formed and valid",
            "stderr_part": ""}),
    ]
)
def test_extractor_pdf_valid(filename, result_dict, evaluate_extractor):
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
        extractor = JHovePdfExtractor(filename=correct.filename,
                                    mimetype="application/pdf")
        extractor.extract()

        evaluate_extractor(extractor, correct)


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
def test_extractor_pdf_invalid(filename, result_dict, evaluate_extractor):
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
        extractor = JHovePdfExtractor(filename=correct.filename,
                                    mimetype="application/pdf")
        extractor.extract()

        evaluate_extractor(extractor, correct)


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
    extractor = JHovePdfExtractor(
        filename=filename,
        mimetype="application/pdf")
    extractor.extract()
    assert f"PDF root version is {version}" in extractor.messages()


def test_pdf_17_scraping_result_ignored():
    """
    Test that JHovePdfExtractor ignores pdf 1.7 scraping results.

    JHove does not support PDF version 1.7, but before running the extractors, we
    don't know what the exact version is. Thus, in case we encounter a PDF 1.7,
    we must ignore the error messages normally produced by JHove and instead
    log a message letting the user know that the scraping result from JHove was
    ignored.
    """
    extractor = JHovePdfExtractor(
        filename=Path("tests/data/application_pdf/valid_1.7.pdf"),
        mimetype="application/pdf")
    extractor.extract()
    assert not extractor.errors()
    assert ("JHove does not support PDF 1.7: All errors and messages ignored."
            in extractor.messages())


@pytest.mark.parametrize(
    ["version_in_filename", "found_version"],
    [
        ["1.2", "1.0"],
        ["1.3", "1.0"],
        ["1.5", "1.1"],
        ["1.6", "1.1"],
        ["A-1a", "1.0"],
    ])
def test_extractor_invalid_pdfversion(version_in_filename, found_version):
    """
    Test that unsupported version is detected.
    """
    extractor = JHovePdfExtractor(
        filename=Path("tests/data/application_pdf/invalid_X_wrong_version"
                      ".pdf".replace("X", version_in_filename)),
        mimetype="application/pdf")
    extractor.extract()
    assert partial_message_included(
        "MIME type application/pdf with version {} is not "
        "supported.".format(found_version), extractor.errors())
    assert not extractor.well_formed


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
def test_extractor_jpeg(filename, result_dict, evaluate_extractor):
    """
    Test jpeg scraping.

    :filename: Test file name
    :result_dict: Result dict containing test purpose, and parts of
                  expected results of stdout and stderr
    """
    correct = parse_results(filename, "image/jpeg",
                            result_dict, True)
    correct.update_mimetype("image/jpeg")
    extractor = JHoveJpegExtractor(filename=correct.filename,
                                 mimetype="image/jpeg")
    extractor.extract()
    correct.streams[0]["version"] = UNAV

    evaluate_extractor(extractor, correct)


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
            "purpose": "Test valid file, which is invalid for this extractor.",
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
def test_extractor_html(filename, result_dict, mimetype, charset,
                      evaluate_extractor):
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

    extractor = JHoveHtmlExtractor(filename=correct.filename,
                                 mimetype=mimetype,
                                 params=correct.params)
    extractor.extract()

    evaluate_extractor(extractor, correct)


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
def test_extractor_wav(filename, result_dict, evaluate_extractor):
    """
    Test wav and bwf scraping.

    :filename: Test file name
    :result_dict: Result dict containing test purpose, and parts of
                  expected results of stdout and stderr
    """
    correct = parse_results(filename, "audio/x-wav",
                            result_dict, True)
    correct.update_mimetype("audio/x-wav")
    extractor = JHoveWavExtractor(filename=correct.filename,
                                mimetype="audio/x-wav")
    extractor.extract()

    evaluate_extractor(extractor, correct)


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
def test_extractor_aiff(filename, result_dict, evaluate_extractor):
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
    extractor = JHoveAiffExtractor(filename=correct.filename,
                                 mimetype="audio/x-aiff")
    extractor.extract()

    evaluate_extractor(extractor, correct)


@pytest.mark.parametrize(
    ["mime", "ver", "class_"],
    [
        ("image/gif", "1989a", JHoveGifExtractor),
        ("image/tiff", "6.0", JHoveTiffExtractor),
        ("image/jpeg", "1.01", JHoveJpegExtractor),
        ("audio/x-wav", "2", JHoveWavExtractor)
    ]
)
def test_is_supported_allow(mime, ver, class_):
    """
    Test is_supported method, allow all versions.

    :mime: MIME type
    :ver: File format version
    :class_: Extractor class to test
    """
    assert class_.is_supported(mime, ver, True)
    assert class_.is_supported(mime, None, True)
    assert not class_.is_supported(mime, ver, False)
    assert class_.is_supported(mime, "foo", True)
    assert not class_.is_supported("foo", ver, True)


@pytest.mark.parametrize(
    ["mime", "ver", "class_"],
    [
        ("application/pdf", "1.4", JHovePdfExtractor),
        ("text/html", "4.01", JHoveHtmlExtractor),
        ("application/xhtml+xml", "1.0", JHoveHtmlExtractor),
    ]
)
def test_is_supported_deny(mime, ver, class_):
    """
    Test is_supported method, allow only known versions.

    :mime: MIME type
    :ver: File format version
    :class_: Extractor class to test
    """
    assert class_.is_supported(mime, ver, True)
    assert class_.is_supported(mime, None, True)
    assert not class_.is_supported(mime, ver, False)
    assert not class_.is_supported(mime, "foo", True)
    assert not class_.is_supported("foo", ver, True)


@pytest.mark.parametrize(
    ["mime", "ver", "class_"],
    [
        ("text/plain", "", JHoveUtf8Extractor)
    ]
)
def test_is_supported_utf8(mime, ver, class_):
    """
    Test is_supported method, utf8 extractor.

    :mime: MIME type
    :ver: File format version
    :class_: Extractor class to test
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
    Test charset parameter in JhoveHtmlExtractor.

    :filename: Test file path
    :mimetype: File MIME type
    :chraset: File character encoding
    :well_formed: Expected well-formed result
    """
    params = {"charset": charset}
    extractor = JHoveHtmlExtractor(filename=Path(filename), mimetype=mimetype,
                                 params=params)
    extractor.extract()
    assert extractor.well_formed == well_formed
    if charset:
        if well_formed:
            assert not extractor.errors()
        else:
            assert partial_message_included(
                "Found encoding declaration", extractor.errors())
    else:
        assert partial_message_included("encoding not defined",
                                        extractor.errors())


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
def test_extractor_epub(filename, result_dict, evaluate_extractor):
    """
    Test EPUB scraping.

    :filename: Test file name
    :result_dict: Result dict containing test purpose, and parts of
                  expected results of stdout and stderr
    """
    correct = parse_results(filename, "application/epub+zip",
                            result_dict, True)
    correct.update_mimetype("application/epub+zip")
    extractor = JHoveEpubExtractor(filename=correct.filename,
                                 mimetype="application/epub+zip")
    extractor.extract()

    evaluate_extractor(extractor, correct)


@pytest.mark.usefixtures("patch_shell_attributes_fx")
def test_jhove_returns_invalid_return_code():
    """Test that a correct error message is given
    when the tool gives an invalid return code"""
    mimetype = "application/pdf"
    path = Path("tests/data", mimetype.replace("/", "_"))
    testfile = path / "valid_1.2.pdf"

    extractor = JHovePdfExtractor(filename=testfile,
                                mimetype=mimetype)

    extractor.extract()

    assert "JHove returned invalid return code: -1\n" in extractor.errors()


def test_jhove_tools():
    """Test extractor tools return correctly something non nullable"""
    extractor = JHovePdfExtractor(filename=Path(""),
                                mimetype="")
    assert extractor.tools()["JHOVE"]["version"][0].isdigit()
