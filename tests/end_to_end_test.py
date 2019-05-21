# -*- coding: utf-8 -*-
"""Integration test for scrapers."""
import os
import shutil

import pytest
from six import iteritems

from file_scraper.scraper import Scraper
from tests.common import get_files

# These files will result (:unav) for some elements
# For GIFs and TIFFs with 3 images inside, the version is missing from the
# second and third streams, but exists in the first one.
# MPEG-TS file contains "menu" stream, where version is None.
# Quicktime file contains a timecode track, where version is None.
UNAV_ELEMENTS = {
    "tests/data/application_x-internet-archive/valid_1.0_.arc.gz": ["version",
                                                                    "version"],
    "tests/data/application_msword/valid_11.0.doc": ["version", "version"],
    "tests/data/application_vnd.ms-excel/valid_11.0.xls": ["version",
                                                           "version"],
    "tests/data/application_vnd.ms-powerpoint/valid_11.0.ppt": ["version",
                                                                "version"],
    "tests/data/application_vnd.oasis.opendocument.formula/valid_1.0"
    ".odf": ["version", "version"],
    "tests/data/application_vnd.openxmlformats-officedocument.presentationml"
    ".presentation/valid_15.0.pptx": ["version", "version"],
    "tests/data/application_vnd.openxmlformats-officedocument.spreadsheetml"
    ".sheet/valid_15.0.xlsx": ["version", "version"],
    "tests/data/application_vnd.openxmlformats-officedocument.word"
    "processingml.document/valid_15.0.docx": ["version", "version"],
    "tests/data/image_gif/valid_1989a.gif": ["version", "version"],
    "tests/data/image_tiff/valid_6.0_multiple_tiffs.tif": [
        "version", "version"],
    "tests/data/video_MP2T/valid_.ts": ["version", "codec_creator_app_version",
                                        "codec_creator_app", "data_rate",
                                        "codec_creator_app_version",
                                        "codec_creator_app", "bits_per_sample",
                                        "codec_creator_app_version",
                                        "codec_creator_app", "version"],
    "tests/data/video_quicktime/valid__dv_wav.mov": ["version", "version",
                                                     "version", "version"],
    "tests/data/audio_mpeg/valid_1.mp3": ["bits_per_sample",
                                          "codec_creator_app_version",
                                          "codec_creator_app"],
    "tests/data/video_mp4/valid__h264_aac.mp4": ["version", "version",
                                                 "bits_per_sample", "version"],
    "tests/data/video_mpeg/valid_1.m1v": ["codec_creator_app_version",
                                          "codec_creator_app"],
    "tests/data/video_mpeg/valid_2.m2v": ["codec_creator_app_version",
                                          "codec_creator_app"]}

# These are actually valid with another mimetype or version
# or due to special parameters or missing scraper
# invalid_1.4_wrong_version.pdf -- is valid PDF 1.7
# invalid__header_corrupted.por -- is valid text/plain
# invalid__truncated.por - is valid text/plain
# invalid_1.0_no_doctype.xhtml - is valid text/xml
# Xml files would require schema or catalog, this is tested in
# unit tests of Xmllint.
IGNORE_INVALID = [
    "tests/data/application_pdf/invalid_1.4_wrong_version.pdf",
    "tests/data/application_x-spss-por/invalid__header_corrupted.por",
    "tests/data/application_x-spss-por/invalid__truncated.por",
    "tests/data/application_xhtml+xml/invalid_1.0_no_doctype.xhtml"]
# XML schema definitions should not be tested.
# The pef with JPEG2000 image is only used for testing that the ghostscript
# version is recent enough to handle it.
IGNORE_VALID = ["tests/data/text_xml/valid_1.0_xsd.xml",
                "tests/data/text_xml/valid_1.0_local_xsd.xml",
                "tests/data/text_xml/valid_1.0_catalog.xml",
                "tests/data/application_pdf/valid_1.6_jpeg2000.pdf"]

# Ignore these we know that warc, arc and dpx files are not currently
# supported for full metadata scraping
IGNORE_FOR_METADATA = IGNORE_VALID + [
    "tests/data/application_warc/valid_0.17.warc",
    "tests/data/application_warc/valid_0.18.warc",
    "tests/data/application_warc/valid_1.0.warc",
    "tests/data/application_warc/valid_1.0_.warc.gz",
    "tests/data/application_x-internet-archive/valid_1.0.arc",
    "tests/data/application_x-internet-archive/valid_1.0_.arc.gz",
    "tests/data/image_x-dpx/valid_2.0.dpx"]

# These invalid files are recognized as application/gzip
DIFFERENT_MIMETYPE_INVALID = {
    "tests/data/application_warc/invalid__missing_data.warc.gz":
        "application/gzip",
    "tests/data/application_x-internet-archive/invalid__missing_data.arc.gz":
        "application/gzip"}


def _assert_valid_scraper_result(scraper, fullname, mimetype, well_formed):
    """Short hand function to assert the scrape result.

    :param scraper: Scraper object instance.
    :param fullname: Full filename in str.
    :param mimetype: Expected mimetype in str.
    :param well_formed: Expected well-formed as either truthy or falsey.
    """
    if well_formed:
        assert scraper.well_formed
    else:
        assert not scraper.well_formed
    assert scraper.mimetype == mimetype
    assert scraper.streams not in [None, {}]

    unavs = []
    for _, stream in iteritems(scraper.streams):
        for key, stream_value in iteritems(stream):
            if stream_value == "(:unav)":
                unavs.append(key)

    if fullname in UNAV_ELEMENTS:
        assert set(unavs) == set(UNAV_ELEMENTS[fullname])
    else:
        assert not unavs


@pytest.mark.parametrize(("fullname", "mimetype"), get_files(well_formed=True))
def test_valid_combined(fullname, mimetype):
    """Integration test for valid files.
    - Test that mimetype matches.
    - Test Find out all None elements.
    - Test that errors are not given.
    - Test that all files are well-formed.
    - Ignore few files because of required parameter or missing scraper.
    """
    if fullname in IGNORE_VALID:
        pytest.skip("[%s] in ignore" % fullname)

    scraper = Scraper(fullname)
    scraper.scrape()

    for _, info in iteritems(scraper.info):
        assert not info["errors"]

    _assert_valid_scraper_result(scraper, fullname, mimetype, True)


@pytest.mark.parametrize(("fullname", "mimetype"),
                         get_files(well_formed=False))
def test_invalid_combined(fullname, mimetype):
    """Integration test for all invalid files.
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

    scraper = Scraper(fullname)
    scraper.scrape()

    for _, info in iteritems(scraper.info):
        if scraper.mimetype != mimetype and info["class"] == "ScraperNotFound":
            pytest.skip(("[%s] mimetype mismatches with scraper "
                         "and scraper not found") % fullname)

    assert scraper.well_formed is False  # Could be also None (wrong)
    assert scraper.mimetype == mimetype or (
        fullname in DIFFERENT_MIMETYPE_INVALID)


@pytest.mark.parametrize(("fullname", "mimetype"), get_files(well_formed=True))
def test_without_wellformed(fullname, mimetype):
    """Test the case where metadata is collected without well-formedness check.
    - Test that well-formed is always None.
    - Test that mimetype matches.
    - Test that there exists correct stream type for image, video, audio
      and text.
    - Test a random element existence for image, video, audio and text.
    """
    if fullname in IGNORE_FOR_METADATA:
        pytest.skip("[%s] in ignore" % fullname)

    scraper = Scraper(fullname)
    scraper.scrape(False)

    _assert_valid_scraper_result(scraper, fullname, mimetype, False)

    mimepart = mimetype.split("/")[0]
    if mimepart in ["image", "video", "text", "audio"]:
        assert mimepart in scraper.streams[0]["stream_type"]

    elem_dict = {"image": "colorspace", "video": "color",
                 "videocontainer": "codec_name",
                 "text": "charset", "audio": "num_channels"}

    for index, stream in iteritems(scraper.streams):
        assert stream["stream_type"] is not None
        if stream["stream_type"] in elem_dict:
            assert elem_dict[stream["stream_type"]] in stream

    if "text/csv" in mimetype:
        assert "delimiter" in scraper.streams[0]


@pytest.mark.parametrize(("fullname", "mimetype"), get_files(well_formed=True))
def test_coded_filename(testpath, fullname, mimetype):
    """Integration test with unicode and utf-8 filename and with all scrapers.
    - Test that unicode filenames work with all mimetypes
    - Test that utf-8 encoded filenames work with all mimetypes
    """
    _ = mimetype
    if fullname in IGNORE_VALID + ["tests/data/text_xml/valid_1.0_dtd.xml"]:
        pytest.skip("[%s] in ignore" % fullname)
    ext = fullname.rsplit(".", 1)[-1]
    unicode_name = os.path.join(testpath, u"äöå.%s" % ext)
    shutil.copy(fullname, unicode_name)
    scraper = Scraper(unicode_name)
    scraper.scrape()
    assert scraper.well_formed
    scraper = Scraper(unicode_name.encode("utf-8"))
    scraper.scrape()
    assert scraper.well_formed
