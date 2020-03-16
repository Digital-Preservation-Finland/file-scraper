# -*- coding: utf-8 -*-
"""
Integration test for scrapers:
    - Scraping with checking the well-formedness for valid files,
      without and with user predefined MIME type and version.
    - Scraping with checking the well-formedness for invalid files.
    - Scraping without checking the well-formedness for valid files,
      without and with user predefined MIME type and version.
    - Scraping with unicode and utf-8 encoded file names.
    - Scraping with user predefined MIME type and version.
    - Scraping with predefined character encoding.
"""
from __future__ import unicode_literals

import os
import shutil

import pytest
from six import iteritems

from file_scraper.scraper import Scraper
from tests.common import get_files

# We currently do not have capability to define the file format version
# of these test files
UNAV_VERSION = [
    "tests/data/application_x-internet-archive/valid_1.0_.arc.gz",
    "tests/data/application_msword/valid_11.0.doc",
    "tests/data/application_vnd.ms-excel/valid_11.0.xls",
    "tests/data/application_vnd.ms-powerpoint/valid_11.0.ppt",
    "tests/data/application_vnd.oasis.opendocument.formula/valid_1.0.odf",
    "tests/data/application_vnd.openxmlformats-officedocument.presentationml"
    ".presentation/valid_15.0.pptx",
    "tests/data/application_vnd.openxmlformats-officedocument.spreadsheetml"
    ".sheet/valid_15.0.xlsx",
    "tests/data/application_vnd.openxmlformats-officedocument.word"
    "processingml.document/valid_15.0.docx",
]

# These files will result (:unav) for some elements
# For GIFs and TIFFs with 3 images inside, the version is missing from the
# second and third streams, but exists in the first one.
# MPEG-TS file contains "menu" stream, where version is None.
# Quicktime file contains a timecode track, where version is None.
UNAV_ELEMENTS = {
    "tests/data/application_x-internet-archive/valid_1.0_.arc.gz": ["version"],
    "tests/data/application_msword/valid_11.0.doc": ["version"],
    "tests/data/application_vnd.ms-excel/valid_11.0.xls": ["version"],
    "tests/data/application_vnd.ms-powerpoint/valid_11.0.ppt": ["version"],
    "tests/data/application_vnd.oasis.opendocument.formula/valid_1.0"
    ".odf": ["version"],
    "tests/data/application_vnd.openxmlformats-officedocument.word"
    "processingml.document/valid_15.0.docx": ["version"],
    "tests/data/image_gif/valid_1989a.gif": ["version", "version"],
    "tests/data/image_tiff/valid_6.0_multiple_tiffs.tif": [
        "version", "version"],
    "tests/data/video_MP2T/valid_.ts": ["codec_creator_app_version",
                                        "codec_creator_app", "data_rate",
                                        "codec_creator_app_version",
                                        "codec_creator_app", "bits_per_sample",
                                        "codec_creator_app_version",
                                        "codec_creator_app",
                                        "mimetype", "version"],
    "tests/data/video_quicktime/valid__dv_wav.mov": ["mimetype", "version",
                                                     "version"],
    "tests/data/video_quicktime/valid__h264_aac.mov": ["bits_per_sample",
                                                       "mimetype", "version"],
    "tests/data/audio_mpeg/valid_1.mp3": ["bits_per_sample",
                                          "codec_creator_app_version",
                                          "codec_creator_app"],
    "tests/data/video_mp4/valid__h264_aac.mp4": ["bits_per_sample"],
    "tests/data/video_mpeg/valid_1.m1v": ["codec_creator_app_version",
                                          "codec_creator_app"],
    "tests/data/video_mpeg/valid_2.m2v": ["codec_creator_app_version",
                                          "codec_creator_app"],
}

# These are actually valid with another mimetype or version
# or due to special parameters or missing scraper
IGNORE_INVALID = [

    # invalid_1.4_wrong_version.pdf -- is valid PDF 1.7
    "tests/data/application_pdf/invalid_1.4_wrong_version.pdf",

    # invalid_1.0_no_doctype.xhtml - is valid text/xml
    # Xml files would require schema or catalog, this is tested in
    # unit tests of Xmllint.
    "tests/data/application_xhtml+xml/invalid_1.0_no_doctype.xhtml",

    # invalid__header_corrupted.por -- is valid text/plain
    "tests/data/application_x-spss-por/invalid__header_corrupted.por",

    # invalid__truncated.por - is valid text/plain
    "tests/data/application_x-spss-por/invalid__truncated.por",

    # invalid__pspp_header.por - PSPP created .pors are not well-formed,
    # but still validate as text/plain
    "tests/data/application_x-spss-por/invalid__pspp_header.por"
]

# XML schema definitions should not be tested.
IGNORE_VALID = [
    "tests/data/text_xml/valid_1.0_xsd.xml",
    "tests/data/text_xml/valid_1.0_local_xsd.xml",
    "tests/data/text_xml/valid_1.0_catalog.xml",
]

# Ignore these we know that warc, arc and dpx files are not currently
# supported for metadata scraping.
IGNORE_FOR_METADATA = IGNORE_VALID + [
    "tests/data/image_x-dpx/valid_2.0.dpx",
    "tests/data/application_warc/valid_1.0_.warc.gz",
    "tests/data/application_x-internet-archive/valid_1.0_.arc.gz",
]

# These invalid files are recognized as application/gzip
DIFFERENT_MIMETYPE_INVALID = {
    "tests/data/application_warc/invalid__missing_data.warc.gz":
        "application/gzip",
    "tests/data/application_x-internet-archive/invalid__missing_data.arc.gz":
        "application/gzip"}

# To get some files validated against the strictest applicable criteria instead
# of just checking that they are indeed text files, the MIME type has to be
# given by the user.
GIVEN_MIMETYPES = {
    "tests/data/text_csv/valid__ascii.csv": "text/csv",
    "tests/data/text_csv/valid__ascii_header.csv": "text/csv",
    "tests/data/text_csv/valid__header_only.csv": "text/csv",
    "tests/data/text_csv/valid__iso8859-15.csv": "text/csv",
    "tests/data/text_csv/valid__utf8.csv": "text/csv",
    "tests/data/text_csv/valid__utf8_header.csv": "text/csv",
    "tests/data/text_csv/valid__iso8859-15_header.csv": "text/csv",
    "tests/data/text_csv/invalid__missing_end_quote.csv": "text/csv",
    "tests/data/text_xml/valid_1.0_mets_noheader.xml": "text/xml",
    "tests/data/text_plain/valid__utf16be_without_bom.txt": "text/plain",
    "tests/data/text_plain/valid__utf16le_without_bom.txt": "text/plain",
    "tests/data/text_plain/valid__utf16be_multibyte.txt": "text/plain",
    "tests/data/text_plain/valid__utf16le_multibyte.txt": "text/plain",
    "tests/data/text_plain/valid__utf32be_without_bom.txt": "text/plain",
    "tests/data/text_plain/valid__utf32le_without_bom.txt": "text/plain",
    "tests/data/text_plain/valid__utf32be_bom.txt": "text/plain",
    "tests/data/text_plain/valid__utf32le_bom.txt": "text/plain",
    "tests/data/text_plain/invalid__utf8_just_c3.txt": "text/plain",
}

# To get some files validated against the strictest applicable criteria the
# charset has to be given by the user.
GIVEN_CHARSETS = {
    "tests/data/text_plain/valid__utf16be_multibyte.txt": "UTF-16",
    "tests/data/text_plain/valid__utf16le_multibyte.txt": "UTF-16",
    "tests/data/text_plain/valid__utf16be_without_bom.txt": "UTF-16",
    "tests/data/text_plain/valid__utf16le_without_bom.txt": "UTF-16",
    "tests/data/text_plain/valid__utf32be_without_bom.txt": "UTF-32",
    "tests/data/text_plain/valid__utf32le_without_bom.txt": "UTF-32",
    "tests/data/text_plain/valid__utf32be_bom.txt": "UTF-32",
    "tests/data/text_plain/valid__utf32le_bom.txt": "UTF-32",
    "tests/data/text_plain/invalid__utf8_just_c3.txt": "UTF-8",
}


def _assert_valid_scraper_result(scraper, fullname, mimetype, version,
                                 well_formed):
    """Short hand function to assert the scrape result.

    :param scraper: Scraper object instance.
    :param fullname: Full filename in str.
    :param mimetype: Expected mimetype in str.
    :param version: Expected version
    :param well_formed: Expected well-formed as either truthy or falsey.
    """
    if well_formed:
        assert scraper.well_formed
    else:
        assert not scraper.well_formed
    assert scraper.mimetype == mimetype
    if not fullname in UNAV_VERSION:
        assert scraper.version == version
    assert scraper.streams not in [None, {}]

    unavs = []
    for _, stream in iteritems(scraper.streams):
        for key, stream_value in iteritems(stream):
            if stream_value == "(:unav)":
                unavs.append(key)

    unav_expected = UNAV_ELEMENTS

    if fullname in unav_expected:
        assert sorted(unavs) == sorted(unav_expected[fullname])
    else:
        assert not unavs


@pytest.mark.parametrize(("fullname", "mimetype", "version"),
                         get_files(well_formed=True))
def test_valid_combined(fullname, mimetype, version):
    """
    Integration test for valid files.
    - Test that mimetype and version matches.
    - Test Find out all None elements.
    - Test that errors are not given.
    - Test that all files are well-formed.
    - Ignore few files because of required parameter or missing scraper.
    - Test that giving the resulted MIME type, version and charset
      produce the same results.
    """
    if fullname in IGNORE_VALID:
        pytest.skip("[%s] in ignore" % fullname)

    predefined_mimetype = GIVEN_MIMETYPES.get(fullname, None)
    predefined_charset = GIVEN_CHARSETS.get(fullname, None)
    scraper = Scraper(fullname, mimetype=predefined_mimetype,
                      charset=predefined_charset)
    scraper.scrape()

    for _, info in iteritems(scraper.info):
        assert not info["errors"]

    _assert_valid_scraper_result(scraper, fullname, mimetype, version, True)

    # Test that output does not change if MIME type and version are given
    # to be the ones scraper would determine them to be in any case.

    # This cannot be done with compressed arcs, as WarctoolsScraper reports
    # the MIME type of the compressed archive instead of application/gzip,
    # so for those types, all required testing is already done here.
    if (scraper.mimetype in ["application/x-internet-archive"] and
            fullname[-3:] == ".gz"):
        return

    given_scraper = Scraper(fullname, mimetype=scraper.mimetype,
                            version=scraper.version,
                            charset=scraper.streams[0].get("charset", None))
    given_scraper.scrape()

    assert given_scraper.mimetype == scraper.mimetype
    assert given_scraper.version == scraper.version
    assert given_scraper.streams == scraper.streams


@pytest.mark.parametrize(("fullname", "mimetype", "version"),
                         get_files(well_formed=False))
# pylint: disable=unused-argument
def test_invalid_combined(fullname, mimetype, version):
    """
    Integration test for all invalid files.
    - Test that well_formed is False and mimetype is expected.
    - If well_formed is None, check that Scraper was not found.
    - Skip files that are known cases where it is identified
      differently (but yet correctly) than expected and would be
      well-formed.
    - Skip empty files, since those are detected as inode/x-empty
      and scraper is not found.
    """
    if "empty" in fullname or fullname in IGNORE_INVALID:
        pytest.skip("[%s] has empty or in invalid ignore" % fullname)

    predefined_mimetype = GIVEN_MIMETYPES.get(fullname, None)
    predefined_charset = GIVEN_CHARSETS.get(fullname, None)
    scraper = Scraper(fullname, mimetype=predefined_mimetype,
                      charset=predefined_charset)
    scraper.scrape()

    for _, info in iteritems(scraper.info):
        if scraper.mimetype != mimetype and info["class"] == "ScraperNotFound":
            pytest.skip(("[%s] mimetype mismatches with scraper "
                         "and scraper not found") % fullname)

    assert scraper.well_formed is False  # Could be also None (wrong)
    assert scraper.mimetype in [mimetype, "(:unav)"] or (
            fullname in DIFFERENT_MIMETYPE_INVALID)


@pytest.mark.parametrize(("fullname", "mimetype", "version"),
                         get_files(well_formed=True))
def test_without_wellformed(fullname, mimetype, version):
    """
    Test the case where metadata is collected without well-formedness check.
    - Test that well-formed is always None.
    - Test that mimetype and version matches.
    - Test that there exists correct stream type for image, video, audio
      and text.
    - Test a random element existence for image, video, audio and text.
    - Test that giving the resulted MIME type, version and charset
      produce the same results.
    """
    if fullname in IGNORE_FOR_METADATA:
        pytest.skip("[%s] in ignore" % fullname)

    predefined_mimetype = GIVEN_MIMETYPES.get(fullname, None)
    predefined_charset = GIVEN_CHARSETS.get(fullname, None)
    scraper = Scraper(fullname, mimetype=predefined_mimetype,
                      charset=predefined_charset)
    scraper.scrape(False)

    _assert_valid_scraper_result(scraper, fullname, mimetype, version, False)

    mimepart = mimetype.split("/")[0]
    if mimepart in ["image", "video", "text", "audio"]:
        assert mimepart in scraper.streams[0]["stream_type"]

    elem_dict = {"image": "colorspace", "video": "color",
                 "videocontainer": "codec_name",
                 "text": "charset", "audio": "num_channels"}

    for stream in scraper.streams.values():
        assert stream["stream_type"] not in ["(:unav)", None]
        if stream["stream_type"] in elem_dict:
            assert elem_dict[stream["stream_type"]] in stream

    # Test that output does not change if MIME type and version are given
    # to be the ones scraper would determine them to be in any case.

    # This cannot be done with compressed arcs, as WarctoolsScraper reports
    # the MIME type of the compressed archive instead of application/gzip,
    # so for those types, all required testing is already done here.
    if (scraper.mimetype in ["application/x-internet-archive"] and
            fullname[-3:] == ".gz"):
        return

    given_scraper = Scraper(fullname, mimetype=scraper.mimetype,
                             version=scraper.version,
                             charset=scraper.streams[0].get("charset", None))
    given_scraper.scrape(False)

    assert given_scraper.mimetype == scraper.mimetype
    assert given_scraper.version == scraper.version
    assert given_scraper.streams == scraper.streams


@pytest.mark.parametrize(("fullname", "mimetype", "version"),
                         get_files(well_formed=True))
# pylint: disable=unused-argument
def test_coded_filename(testpath, fullname, mimetype, version):
    """
    Integration test with unicode and utf-8 filename and with all scrapers.
    - Test that unicode filenames work with all mimetypes
    - Test that utf-8 encoded filenames work with all mimetypes
    """
    if fullname in IGNORE_VALID + ["tests/data/text_xml/valid_1.0_dtd.xml"]:
        pytest.skip("[%s] in ignore" % fullname)
    if fullname in GIVEN_CHARSETS:
        pytest.skip("[%s] in ignore" % fullname)
    ext = fullname.rsplit(".", 1)[-1]
    unicode_name = os.path.join(testpath, "äöå.%s" % ext)
    shutil.copy(fullname, unicode_name)
    scraper = Scraper(unicode_name)
    scraper.scrape()
    assert scraper.well_formed
    scraper = Scraper(unicode_name.encode("utf-8"))
    scraper.scrape()
    assert scraper.well_formed


@pytest.mark.parametrize(
    ["filepath", "params", "well_formed", "expected_mimetype",
     "expected_version", "expected_charset"],
    [
        # Give the correct MIME type, let scrapers handle version
        ("tests/data/image_tiff/valid_6.0.tif", {"mimetype": "image/tiff"},
         True, "image/tiff", "6.0", None),

        # Give the correct MIME type with unsupported version, resulting
        # in not well-formed file
        ("tests/data/image_tiff/valid_6.0.tif",
         {"mimetype": "image/tiff", "version": "99.9"},
         False, "image/tiff", "6.0", None),

        # Give the correct MIME type with a supported but incorrect version:
        # file is reported as not well-formed.
        ("tests/data/image_gif/valid_1987a.gif",
         {"mimetype": "image/gif", "version": "1989a"},
         False, "image/gif", "1987a", None),

        # Give the correct MIME type with another accepted version:
        # file is reported as well-formed
        ("tests/data/application_pdf/valid_A-1a.pdf",
         {"mimetype": "application/pdf", "version": "1.4"},
         True, "application/pdf", "1.4", None),

        # Give unsupported MIME type, resulting in not well-formed
        ("tests/data/image_tiff/valid_6.0.tif", {"mimetype": "audio/mpeg"},
         False, "(:unav)", "(:unav)", None),

        # Give the correct MIME type but wrong charset
        ("tests/data/text_plain/valid__utf8_bom.txt",
         {"mimetype": "text/plain", "charset": "UTF-16"},
         False, "text/plain", "(:unap)", "UTF-16"),

        # Give the correct MIME type and charset, but wrong version
        ("tests/data/text_html/valid_4.01.html",
         {"mimetype": "text/html", "version": "0.0", "charset": "UTF-8"},
         False, "(:unav)", "(:unav)", "UTF-8"),

        # Scrape invalid XML as plaintext, as which it is well-formed
        ("tests/data/text_xml/invalid_1.0_no_closing_tag.xml",
         {"mimetype": "text/plain"}, True, "text/plain", "(:unap)", "UTF-8"),

        # Scrape invalid HTML as plaintext, as which it is well-formed
        ("tests/data/text_html/invalid_5.0_illegal_tags.html",
         {"mimetype": "text/plain"}, True, "text/plain", "(:unap)", "UTF-8"),

        # Scrape invalid HTML as plaintext and give correct charset, as which
        # it is well-formed
        ("tests/data/text_html/invalid_5.0_illegal_tags.html",
         {"mimetype": "text/plain", "charset": "UTF-8"}, True,
         "text/plain", "(:unap)", "UTF-8"),

        # Scrape invalid HTML as plaintext and give incorrect charset, as
        # which it is not well-formed
        ("tests/data/text_html/invalid_5.0_illegal_tags.html",
         {"mimetype": "text/plain", "charset": "UTF-16"}, False,
         "text/plain", "(:unap)", "UTF-16"),

        # Scrape a random text file as HTML, as which it is not well-formed
        ("tests/data/text_plain/valid__utf8_without_bom.txt",
         {"mimetype": "text/html"}, False, "(:unav)", "(:unav)", "UTF-8"),

        # Scrape a file with MIME type that can produce "well-formed" result
        # from some scrapers, but combining the results should reveal the file
        # as not well-formed
        ("tests/data/image_gif/valid_1987a.gif", {"mimetype": "image/png"},
         False, "image/gif", "(:unav)", None),

        # We assume that application/gzip is either gzipped ARC or WARC
        ("tests/data/application_x-internet-archive/valid_1.0_.arc.gz",
         {"mimetype": "application/gzip"}, True,
         "application/x-internet-archive", "(:unav)", None),
    ]
)
def test_given_filetype(filepath, params, well_formed, expected_mimetype,
                        expected_version, expected_charset):
    """
    Test the scraping to be done as user given file type.

    MIME type and version results are checked both directly from the scraper
    and for well-formed files also from the first stream. In addition to this,
    well-formedness status of the file should be as expected.

    :filepath: Test file path
    :params: Parameters for Scraper
    :well_formed: Expected result of well-formedness
    :expected_mimetype: Expected MIME type result
    :exprected_version: Expected file format version
    """
    scraper = Scraper(filename=filepath, **params)
    scraper.scrape()

    assert scraper.well_formed == well_formed
    assert scraper.mimetype == expected_mimetype
    assert scraper.version == expected_version
    if expected_charset:
        assert scraper.streams[0]["charset"] == expected_charset
    else:
        assert "charset" not in scraper.streams[0]

    assert scraper.streams[0]["mimetype"] == expected_mimetype
    assert scraper.streams[0]["version"] == expected_version


@pytest.mark.parametrize(
    ["filepath", "charset", "well_formed"],
    [("tests/data/text_plain/valid__utf8_without_bom.txt", "UTF-8", True),
     ("tests/data/text_plain/valid__utf8_without_bom.txt", "utf-8", True),
     ("tests/data/text_plain/valid__utf8_without_bom.txt", "UTF-16", False),
     ("tests/data/text_plain/valid__utf8_bom.txt", "UTF-8", True),
     ("tests/data/text_plain/valid__utf8_bom.txt", "UTF-16", False),
     ("tests/data/text_plain/valid__utf16be_without_bom.txt", "UTF-8", False),
     ("tests/data/text_plain/valid__utf16be_without_bom.txt", "UTF-16", True),
     ("tests/data/text_plain/valid__utf16be_bom.txt", "UTF-8", False),
     ("tests/data/text_plain/valid__utf16be_bom.txt", "UTF-16", True),
     ("tests/data/text_plain/valid__utf16le_without_bom.txt", "UTF-8", False),
     ("tests/data/text_plain/valid__utf16le_without_bom.txt", "UTF-16", True),
     ("tests/data/text_plain/valid__utf16le_bom.txt", "UTF-8", False),
     ("tests/data/text_plain/valid__utf16le_bom.txt", "UTF-16", True),
     ("tests/data/text_plain/valid__utf32be_without_bom.txt", "UTF-32", True),
     ("tests/data/text_plain/valid__utf32be_without_bom.txt", "UTF-16", False),
     ("tests/data/text_plain/valid__utf32be_bom.txt", "UTF-32", True),
     ("tests/data/text_plain/valid__utf32be_bom.txt", "UTF-16", False),
     ("tests/data/text_plain/valid__utf32le_without_bom.txt", "UTF-32", True),
     ("tests/data/text_plain/valid__utf32le_without_bom.txt", "UTF-16", False),
     ("tests/data/text_plain/valid__utf32le_bom.txt", "UTF-32", True),
     ("tests/data/text_plain/valid__utf32le_bom.txt", "UTF-16", False),
     ("tests/data/text_plain/valid__iso8859.txt", "ISO-8859-15", True),
     ("tests/data/text_plain/valid__iso8859.txt", "UTF-16", False),
     ("tests/data/text_xml/valid_1.0_well_formed.xml", "UTF-8", True),
     ("tests/data/text_xml/valid_1.0_well_formed.xml", "UTF-16", False),
     ("tests/data/text_html/valid_4.01.html", "ISO-8859-15", False),
     ("tests/data/text_html/valid_4.01.html", "UTF-8", True),
     ("tests/data/application_xhtml+xml/valid_1.0.xhtml", "UTF-8", True),
     ("tests/data/application_xhtml+xml/valid_1.0.xhtml", "UTF-16", False),
     ("tests/data/text_csv/valid__ascii.csv", "UTF-8", True),
     ("tests/data/text_csv/valid__ascii.csv", "ISO-8859-15", True),
     ("tests/data/text_csv/valid__ascii.csv", "UTF-16", False),
     ("tests/data/text_plain/valid__utf16be_multibyte.txt", "UTF-16", True),
     ("tests/data/text_plain/valid__utf16be_multibyte.txt", "UTF-8", False),
     ("tests/data/text_plain/valid__utf16le_multibyte.txt", "UTF-16", True),
     ("tests/data/text_plain/valid__utf16le_multibyte.txt", "UTF-8", False),
     ("tests/data/text_plain/invalid__utf8_just_c3.txt", "UTF-8", False),
     ]
)
def test_charset(filepath, charset, well_formed):
    """
    Test charset parameter.

    We are able to give charset as a parameter. This tests the
    parameter with different mimetypes and charset inputs.

    :filepath: Test file path
    :charset: Given and expected character encoding of a test file
    :well_formed: Expected result of well-formedness
    """
    predefined_mimetype = GIVEN_MIMETYPES.get(filepath, None)
    scraper = Scraper(filepath, mimetype=predefined_mimetype,
                      charset=charset)
    scraper.scrape()

    assert scraper.well_formed == well_formed
    assert scraper.streams[0]["charset"] == charset
