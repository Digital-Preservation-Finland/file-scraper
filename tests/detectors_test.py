"""
Tests for Fido and Magic detectors.

This module tests that:
    - FidoDetector and MagicDetector detect MIME types correctly.
    - FidoDetector returns an empty dict from get_important() with
      certain mimetypes and MagicDetector returns certain mimetypes.
    - VerapdfDetector detects PDF/A MIME types and versions but no others.
    - VerapdfDetector results are important for PDF/A files.
    - ExifToolDetector detects the MIME types correctly for tiff and dng files.
    - ExifToolDetector results are important only for dng files.
    - Character encoding detection works properly.
"""
from __future__ import unicode_literals
import time
import pytest
from fido.fido import Fido
from file_scraper.detectors import (_FidoReader,
                                    FidoDetector,
                                    MagicCharset,
                                    MagicDetector,
                                    VerapdfDetector,
                                    ExifToolDetector,
                                    SegYDetector,
                                    SiardDetector)
from file_scraper.defaults import UNKN
from tests.common import get_files, partial_message_included

CHANGE_FIDO = {
    "text_plain/valid__ascii.txt": None,
    "text_plain/valid__iso8859.txt": None,
    "text_plain/valid__utf8_bom.txt": None,
    "text_plain/valid__utf8_without_bom.txt": None,
    "text_plain/valid__utf16le_bom.txt": None,
    "text_plain/valid__utf16le_without_bom.txt": None,
    "text_plain/valid__utf16be_bom.txt": None,
    "text_plain/valid__utf16be_without_bom.txt": None,
    "text_plain/valid__utf32le_bom.txt": None,
    "text_plain/valid__utf32le_without_bom.txt": None,
    "text_plain/valid__utf32be_bom.txt": None,
    "text_plain/valid__utf32be_without_bom.txt": None,
    "text_plain/valid__utf16le_multibyte.txt": None,
    "text_plain/valid__utf16be_multibyte.txt": None,
    "text_plain/valid__utf8_multibyte.txt": None,
    "video_mp4/valid__h264_aac.mp4": None,
    "video_mp4/valid__h264_aac_mp42.mp4": None,
    "application_msword/valid_97-2003.doc": None,
    "application_vnd.openxmlformats-officedocument.spreadsheetml"
    ".sheet/valid_2007 onwards.xlsx": None,
    "application_vnd.openxmlformats-officedocument.presentationml"
    ".presentation/valid_2007 onwards.pptx": None,
    "application_vnd.oasis.opendocument.formula/valid_1.0.odf":
        "application/zip",
    "application_warc/valid_1.0_.warc.gz": "application/gzip",
    "application_mxf/valid__jpeg2000.mxf": None,
    "application_mxf/valid__jpeg2000_grayscale.mxf": None,
    "application_mxf/valid__jpeg2000_lossless.mxf": None,
    "application_mxf/valid__jpeg2000_lossless-wavelet_lossy-"
    "subsampling.mxf": None,
    "text_csv/valid__ascii.csv": None,
    "text_csv/valid__quotechar.csv": None,
    "text_csv/valid__ascii_header.csv": None,
    "text_csv/valid__header_only.csv": None,
    "text_csv/valid__iso8859-15.csv": None,
    "text_csv/valid__utf8.csv": None,
    "text_csv/valid__utf8_header.csv": None,
    "text_csv/valid__iso8859-15_header.csv": None,
    "text_xml/valid_1.0_mets_noheader.xml": None,
    "video_dv/valid__pal_lossy.dv": None,
    "image_x-adobe-dng/valid_1.4.dng": "image/tiff",
    "audio_x-aiff/valid_1.3.aiff": None,
    "application_x-siard/valid_2.1.1.siard": "application/zip",
    "video_x-ms-asf/valid__vc1.wmv": None,
    "video_x-ms-asf/valid__vc1_wma9.wmv": None,
    "image_x-dpx/valid_1.0_just_version_change_from_2.0.dpx": None,
    "text_plain/valid__1.json": None
}

CHANGE_MAGIC = {
    "text_plain/valid__utf16le_without_bom.txt":
        "application/octet-stream",
    "text_plain/valid__utf16be_without_bom.txt":
        "application/octet-stream",
    "text_plain/valid__utf16le_multibyte.txt":
        "application/octet-stream",
    "text_plain/valid__utf16be_multibyte.txt":
        "application/octet-stream",
    "text_plain/valid__utf32le_bom.txt":
        ["application/octet-stream", "text/plain"],
    "text_plain/valid__utf32le_without_bom.txt":
        "application/octet-stream",
    "text_plain/valid__utf32be_bom.txt":
        ["application/octet-stream", "text/plain"],
    "text_plain/valid__utf32be_without_bom.txt":
        "application/octet-stream",
    "video_MP1S/valid__ps1.mpg": "video/mpeg",
    "video_MP2P/valid__ps2.mpg": "video/mpeg",
    "video_MP2T/valid__mpeg2_mp3.ts": "application/octet-stream",
    "application_xhtml+xml/valid_1.0.xhtml": "text/xml",
    "application_warc/valid_1.0_.warc.gz": ["application/x-gzip",
                                            "application/gzip"],
    "application_x-spss-por/valid__spss24-dot.por": "text/plain",
    "application_x-spss-por/valid__spss24-dates.por": "text/plain",
    "text_csv/valid__ascii.csv": ["text/plain", "application/csv"],
    "text_csv/valid__quotechar.csv": "text/plain",
    "text_csv/valid__ascii_header.csv": ["text/plain", "application/csv"],
    "text_csv/valid__header_only.csv": "text/plain",
    "text_csv/valid__iso8859-15.csv": "text/plain",
    "text_csv/valid__utf8.csv": "text/plain",
    "text_csv/valid__utf8_header.csv": "text/plain",
    "text_csv/valid__iso8859-15_header.csv": "text/plain",
    "text_xml/valid_1.0_mets_noheader.xml": "text/plain",
    "application_gml+xml/valid__x-fmt-227.xml": "text/xml",
    "application_gml+xml/valid_3.2_fmt-1047.xml": "text/xml",
    "video_quicktime/valid__h264_aac_no_ftyp_atom.mov":
        "application/octet-stream",
    "image_x-adobe-dng/valid_1.4.dng": "image/tiff",
    "application_x-siard/valid_2.1.1.siard": "application/zip"
}


def test_fido_format_caching():
    """Tests that caching works as if no caching has been used."""
    fido_object = Fido(quiet=True, format_files=["formats-v95.xml",
                                                 "format_extensions.xml"])
    start_time = time.time()
    for _ in range(200):
        reader = _FidoReader('non_existing_file.xml')
        # If caching works, the time spent to initialize the _FidoReader should
        # not take long so 30 seconds would be the absolute max.
        elapsed_time = time.time() - start_time
        assert elapsed_time < 30

        # We're constraining to len for assert, because these three attributes
        # contains large amount of lxml element-objects and thus would
        # make comparison very slow.
        assert len(reader.puid_format_map) == len(fido_object.puid_format_map)
        assert len(reader.formats) == len(fido_object.formats)
        assert len(reader.puid_has_priority_over_map) == len(
            fido_object.puid_has_priority_over_map)


def test_fido_cache_halting_file(fido_cache_halting_file):
    """Tests that time used between raw Fido usage and FidoDetector usage does
    not provide big difference in processing time."""
    fido_object = Fido(quiet=True, format_files=["formats-v95.xml",
                                                 "format_extensions.xml"])
    fido_start_time = time.time()
    fido_object.identify_file(fido_cache_halting_file)
    fido_elapsed_time = time.time() - fido_start_time

    fido_reader_start_time = time.time()
    fido_reader_object = FidoDetector(fido_cache_halting_file)
    fido_reader_object.detect()
    fido_reader_elapsed_time = time.time() - fido_reader_start_time

    # 2 second difference is acceptable with the given test file.
    assert abs(fido_elapsed_time - fido_reader_elapsed_time) < 2


@pytest.mark.parametrize(
    ["filepath", "mimetype", "version", "message"],
    [
        ("application_pdf/valid_1.4.pdf", None, None,
         "INFO: File is not PDF/A, so PDF/A validation is not performed"),
        ("application_pdf/valid_A-1a.pdf", "application/pdf",
         "A-1a", "PDF/A version detected by veraPDF."),
        ("application_pdf/valid_A-2b.pdf", "application/pdf",
         "A-2b", "PDF/A version detected by veraPDF."),
        ("application_pdf/valid_A-3b.pdf", "application/pdf",
         "A-3b", "PDF/A version detected by veraPDF."),
        ("application_pdf/valid_A-3b_no_file_extension", "application/pdf",
         "A-3b", "PDF/A version detected by veraPDF."),
        ("image_png/valid_1.2.png", None, None,
         "INFO: File is not PDF/A, so PDF/A validation is not performed")
    ]
)
def test_pdf_detector(filepath, mimetype, version, message):
    """
    Test that VerapdfDetector works.

    The detector should detect the file types of PDF/A files, but return None
    for other files, including PDF files that are not PDF/A.

    :filepath: Test file
    :mimetype: Expected MIME type
    :version: Exprected file format version
    """
    detector = VerapdfDetector('tests/data/' + filepath)
    detector.detect()
    assert detector.mimetype == mimetype
    assert detector.version == version
    assert message in detector.info['messages']


@pytest.mark.parametrize(
        ["filepath", "mimetype"],
        [
            ("image_x-adobe-dng/valid_1.4.dng", "image/x-adobe-dng"),
            ("image_tiff/valid_6.0.tif", "image/tiff"),
        ]
)
def test_dng_detector(filepath, mimetype):
    """
    Test that ExifToolDetector works with dng and tiff files. ExifToolDetector
    should detect the mimetype of a file and distinct dng files from tiff
    files.

    :filepath: Test file
    :mimetype: Expected mimetype
    """
    detector = ExifToolDetector('tests/data/' + filepath)
    detector.detect()
    assert detector.mimetype == mimetype


@pytest.mark.parametrize(
    ["detector_class", "change_dict"],
    [
        (FidoDetector, CHANGE_FIDO),
        (MagicDetector, CHANGE_MAGIC)
    ]
)
def test_detectors(detector_class, change_dict):
    """Test Fido and Magic detectors.

    The test compares detected mimetype to expected mimetype.
    Runs all well-formed files in the test data set.

    :detector_class: Detector class to test
    :change_dict: Known exceptions to expected mimetypes
    """
    for filename, expected_mimetype, _ in get_files(well_formed=True):

        detector = detector_class(filename)
        detector.detect()

        format_name = filename.replace('tests/data/', '')
        if format_name in change_dict:
            expected_mimetype = change_dict[format_name]

        assertion_message = ("Detected mimetype did not match expected: "
                             "{}: {}".format(
                                 detector_class.__name__, format_name))

        # If the "file" command detects mime types differently in EL7 and EL9,
        # expected_mimetype will be a list. get_files could be made to always
        # return a list of mime types, but this is a quick fix.
        # TODO: This test can be changed back to how it was in commit ff890511
        # after we drop support for EL7.
        if type(expected_mimetype) == list:
            assert any(detector.mimetype == exp_mt for exp_mt in
                       expected_mimetype), assertion_message
        else:
            assert detector.mimetype == expected_mimetype, assertion_message


@pytest.mark.parametrize(
    ["filepath", "important"],
    [
        ("tests/data/application_pdf/valid_A-1a.pdf", True),
        ("tests/data/application_pdf/valid_1.4.pdf", False),
        ("tests/data/image_gif/valid_1987a.gif", False)
    ]
)
def test_important_pdf(filepath, important):
    """
    Test that VerapdfDetector results are important for PDF/A files only.

    :filepath: Test file
    :important: Expected boolean result of important
    """
    detector = VerapdfDetector(filepath)
    detector.detect()
    if important:
        assert "mimetype" in detector.get_important()
        assert "version" in detector.get_important()
    else:
        assert detector.get_important() == {}


@pytest.mark.parametrize(
    ["filepath", "important"],
    [
        ("tests/data/image_x-adobe-dng/valid_1.4.dng", True),
        ("tests/data/image_tiff/valid_6.0.tif", False)
    ]
)
def test_important_dng(filepath, important):
    """
    Test that ExifToolDetector results are important for dng files only.

    :filepath: Test file
    :important: Expected boolean result of important
    """
    detector = ExifToolDetector(filepath)
    detector.detect()
    if important:
        assert "mimetype" in detector.get_important()
    else:
        assert detector.get_important() == {}


@pytest.mark.parametrize(
    ["detector_class", "mimetype"],
    [
        (FidoDetector, "text/html"),
        (FidoDetector, "application/zip"),
        (MagicDetector, "application/vnd.oasis.opendocument.formula")
    ]
)
def test_important_other(detector_class, mimetype):
    """
    Test important with crucial mimetypes using other detectors.

    :detector_class: Detector class
    :mimetype: File MIME type
    """
    detector = detector_class("testfilename")
    detector.mimetype = mimetype
    if detector_class == FidoDetector:
        assert detector.get_important() == {}
    else:
        assert detector.get_important() == {"mimetype": mimetype}


@pytest.mark.parametrize(
    ["filename", "charset"],
    [("tests/data/text_plain/valid__utf8_without_bom.txt", "UTF-8"),
     ("tests/data/text_plain/valid__utf16le_bom.txt", "UTF-16"),
     ("tests/data/text_plain/valid__iso8859.txt", "ISO-8859-15"),
     ("tests/data/video_dv/valid__pal_lossy.dv", None)]
)
def test_magic_charset(filename, charset):
    """
    Test charset encoding detection.

    :filename: Test file
    :charset: Character encoding
    """
    detector = MagicCharset(filename)
    detector.detect()
    if charset:
        detector.charset = charset
        assert not detector.info["errors"]
        assert partial_message_included(
            "Character encoding detected as", detector.info["messages"])
    else:
        assert partial_message_included(
            "Unable to detect character encoding", detector.info["errors"])


@pytest.mark.parametrize(
        ["filepath", "mimetype", "version"],
        [
            # The SEG-Y test files only contain the bare minimum data
            # (i.e. SEG-Y magic number and file format version) in order
            # to be detected by SegYDetector.
            ("application_x.fi-dpres.segy/invalid__ascii_header.sgy",
             "application/x.fi-dpres.segy",
             UNKN),
            ("application_x.fi-dpres.segy/invalid_1.0_ascii_header.sgy",
             "application/x.fi-dpres.segy",
             "1.0"),
            ("application_x.fi-dpres.segy/invalid_2.0_ascii_header.sgy",
             "application/x.fi-dpres.segy",
             "2.0"),
            ("application_x.fi-dpres.segy/invalid__ebcdic_header.sgy",
             "application/x.fi-dpres.segy",
             UNKN),
            ("application_x.fi-dpres.segy/invalid_1.0_ebcdic_header.sgy",
             "application/x.fi-dpres.segy",
             "1.0"),
            ("application_x.fi-dpres.segy/invalid_2.0_ebcdic_header.sgy",
             "application/x.fi-dpres.segy",
             "2.0"),
            ("application_x.fi-dpres.segy/invalid__ebcdic_ljust.sgy",
             "application/x.fi-dpres.segy",
             UNKN),
        ]
)
def test_segy_detector(filepath, mimetype, version):
    """
    Test that works with SEG-Y files. SegYDetector
    should detect the mimetype and, if possible, version of a SEG-Y file.

    :filepath: Test file
    :mimetype: Expected mimetype
    """
    detector = SegYDetector('tests/data/' + filepath)
    detector.detect()
    assert detector.mimetype == mimetype
    assert detector.version == version
    if version == UNKN:
        assert partial_message_included(
            "SEG-Y signature is missing", detector.info["messages"])


@pytest.mark.parametrize(
        ["filepath", "mimetype", "version"],
        [
            ("application_x-siard/valid_2.1.1.siard",
             "application/x-siard",
             "2.1.1"),
        ]
)
def test_siard_detector(filepath, mimetype, version):
    """
    Test that works with SIARD files. SiardDetector
    should detect the mimetype and version of a SIARD file.

    :filepath: Test file
    :mimetype: Expected mimetype
    """
    detector = SiardDetector('tests/data/' + filepath)
    detector.detect()
    assert detector.mimetype == mimetype
    assert detector.version == version
