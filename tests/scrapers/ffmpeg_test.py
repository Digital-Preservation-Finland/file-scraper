"""
Test module for ffmpeg.py

This module tests that:
    - For valid audio and video files the scraping is reported as successful,
      the file is well-formed and metadata is scraped correctly.
    - For empty files the results are similar but file is not well-formed
      and errors should contain an error message. The error message should
      contain the following string:
        - With video/x-matroska, video/mpeg, video/mp4, video/MP2T files:
          "Invalid data found when processing input".
        - With audio/mpeg files: "could not find codec parameters"
        - With video/dv files: "Cannot find DV header"
    - For invalid files the file is not well-formed and errors should contain
      an error message. With the files with missing data the error message
      should contain the following string:
        - With video/x-matroska files: "Truncating packet of size"
        - With video/mpeg and video/mp4 files: "end mismatch"
        - With video/MP2T files: "invalid new backstep"
        - With audio/mpeg files: "Error while decoding stream"
        - With video/dv files: "AC EOB marker is absent"
    - For mp3 files with wrong version reported in the header, the file is not
      well-formed and errors should contain "Error while decoding stream".
    - The mimetypes tested are:
        - video/quicktime containing dv video and pcm (wav) audio stream
        - video/x-matroska containing ffv1 video stream
        - video/dv
        - video/mpeg, with version 1 and 2 separately
        - video/mp4 containing h264 video and aac audio streams
        - video/MP2T file
        - audio/mpeg version 1 file
        - video/avi
        - video/mxf
    - Whether well-formed check is performed or not, the scraper reports the
      following combinations of mimetypes and versions as supported:
        - video/mpeg, "1" or None
        - video/mp4, "" or None
        - video/MP1S, "" or None
        - video/MP2P, "" or None
        - video/MP2T, "" or None
    - A made up version with supported MIME type is reported as supported.
    - A made up MIME type with supported version is reported as not supported.
    - Supported MIME type is supported when well-formedness is not checked.
    - Scraping is done also when well-formedness is not checked.
"""
from __future__ import unicode_literals

import pytest

from file_scraper.ffmpeg.ffmpeg_scraper import FFMpegScraper
from tests.common import parse_results
from tests.scrapers.stream_dicts import (
    AVI_CONTAINER,
    AVI_JPEG2000_VIDEO,
    MXF_CONTAINER,
    MXF_JPEG2000_VIDEO,
    )

NO_METADATA = {0: {'index': 0, 'version': '(:unav)', 'stream_type': '(:unav)'}}
UNAV_MIME = []


@pytest.mark.parametrize(
    ["filename", "result_dict", "mimetype"],
    [
        ("valid__dv_wav.mov", {
            "purpose": "Test valid MOV with DV and WAV.",
            "stdout_part": "file was analyzed successfully",
            "stderr_part": ""},
         "video/quicktime"),
        ("valid.dv", {
            "purpose": "Test valid DV.",
            "stdout_part": "file was analyzed successfully",
            "stderr_part": ""},
         "video/dv"),
        ("valid_4_ffv1.mkv", {
            "purpose": "Test valid MKV.",
            "stdout_part": "file was analyzed successfully",
            "stderr_part": ""},
         "video/x-matroska"),
        ("valid_1.m1v", {
            "purpose": "Test valid MPEG-1.",
            "stdout_part": "file was analyzed successfully",
            "stderr_part": ""},
         "video/mpeg"),
        ("valid_2.m2v", {
            "purpose": "Test valid MPEG-2.",
            "stdout_part": "file was analyzed successfully",
            "stderr_part": ""},
         "video/mpeg"),
        ("valid__h264_aac.mp4", {
            "purpose": "Test valid mp4.",
            "stdout_part": "file was analyzed successfully",
            "stderr_part": ""},
         "video/mp4"),
        ("valid_1.mp3", {
            "purpose": "Test valid mp3.",
            "stdout_part": "file was analyzed successfully",
            "stderr_part": ""},
         "audio/mpeg"),
        ("valid_.ts", {
            "purpose": "Test valid MPEG-TS.",
            "stdout_part": "file was analyzed successfully",
            "stderr_part": ""},
         "video/MP2T"),
    ])
def test_ffmpeg_valid_simple(filename, result_dict, mimetype,
                             evaluate_scraper):
    """
    Test FFMpegScraper with valid files when no metadata is scraped.

    :filename: Test file name
    :result_dict: Result dict containing, test purpose, and parts of
                  expected results of stdout and stderr
    :mimetype: Given and expected mimetype
    """
    correct = parse_results(filename, mimetype, result_dict, True)
    correct.streams.update(NO_METADATA)

    scraper = FFMpegScraper(filename=correct.filename, mimetype=mimetype)
    scraper.scrape_file()

    evaluate_scraper(scraper, correct)


@pytest.mark.parametrize(
    ["filename", "result_dict", "mimetype"],
    [
        # TODO codec_quality testing for both avi files
        ("valid__JPEG2000.avi", {
            "purpose": "Test valid AVI.",
            "stdout_part": "file was analyzed successfully",
            "stderr_part": "",
            "streams": {0: AVI_CONTAINER.copy(),
                        1: AVI_JPEG2000_VIDEO.copy()}},
         "video/avi"),
        ("valid__JPEG2000_lossless-wavelet_lossy-subsampling.avi", {
            "purpose": ("Test valid AVI/JPEG2000 with lossless wavelet "
                        "transform and chroma subsampling."),
            "stdout_part": "file was analyzed successfully",
            "stderr_part": "",
            "streams": {0: AVI_CONTAINER.copy(),
                        1: dict(AVI_JPEG2000_VIDEO.copy(),
                                **{"data_rate": "3.559952",
                                   "codec_quality": "lossless"})}},
         "video/avi"),
        ("valid__JPEG2000_lossless.avi", {
            "purpose": ("Test valid AVI/JPEG2000 with lossless wavelet "
                        "transform and no chroma subsampling."),
            "stdout_part": "file was analyzed successfully",
            "stderr_part": "",
            "streams": {0: AVI_CONTAINER.copy(),
                        1: dict(AVI_JPEG2000_VIDEO.copy(),
                                **{"data_rate": "10.11328",
                                   "sampling": "(:unap)",
                                   "codec_quality": "lossless"})}},
         "video/avi"),
        ("valid__jpeg2000.mxf", {
            "purpose": "Test valid MXF.",
            "stdout_part": "file was analyzed successfully",
            "stderr_part": "",
            "streams": {0: MXF_CONTAINER.copy(),
                        1: MXF_JPEG2000_VIDEO.copy()}},
         "application/mxf"),
        ("valid__jpeg2000_grayscale.mxf", {
            "purpose": "Test valid MXF.",
            "stdout_part": "file was analyzed successfully",
            "stderr_part": "",
            "streams": {0: MXF_CONTAINER.copy(),
                        1: dict(MXF_JPEG2000_VIDEO.copy(),
                                **{"data_rate": "2.21007",
                                   "color": "Grayscale",
                                   "sampling": "(:unap)"})}},
         "application/mxf"),
    ])
def test_ffmpeg_scraper_valid(filename, result_dict, mimetype,
                              evaluate_scraper):
    """
    Test FFMpegScraper with valid files when metadata is scraped.

    :filename: Test file name
    :result_dict: Result dict containing, test purpose, and parts of
                  expected results of stdout and stderr
    :mimetype: Given and expected mimetype
    """
    correct = parse_results(filename, mimetype, result_dict, True)

    scraper = FFMpegScraper(filename=correct.filename, mimetype=mimetype)
    scraper.scrape_file()
    # TODO remove these when mxf testing is added and made functional
#    from file_scraper.utils import generate_metadata_dict
#    print generate_metadata_dict([scraper.streams], [])
#    for stream in range(len(scraper.streams)):
#        print "scraper: " + scraper.streams[stream].stream_type()
#        print "correct: " + correct.streams[stream]["stream_type"]

    evaluate_scraper(scraper, correct)


@pytest.mark.parametrize(
    ["filename", "result_dict", "mimetype"],
    [
        ("invalid_4_ffv1_missing_data.mkv", {
            "purpose": "Test truncated MKV.",
            "stdout_part": "",
            "stderr_part": "Truncating packet of size"}, "video/x-matroska"),
        ("invalid__empty.mkv", {
            "purpose": "Test empty MKV.",
            "stdout_part": "",
            "stderr_part": "Invalid data found when processing input"},
         "video/x-matroska"),
        ("invalid__missing_data.dv", {
            "purpose": "Test truncated DV.",
            "stdout_part": "",
            "stderr_part": "AC EOB marker is absent"},
         "video/dv"),
        ("invalid__empty.dv", {
            "purpose": "Test empty DV.",
            "stdout_part": "",
            "stderr_part": "Cannot find DV header"},
         "video/dv"),
        ("invalid_1_missing_data.m1v", {
            "purpose": "Test invalid MPEG-1.",
            "stdout_part": "",
            "stderr_part": "end mismatch"}, "video/mpeg"),
        ("invalid_1_empty.m1v", {
            "purpose": "Test empty MPEG-1.",
            "stdout_part": "",
            "stderr_part": "Invalid data found when processing input"},
         "video/mpeg"),
        ("invalid_2_missing_data.m2v", {
            "purpose": "Test invalid MPEG-2.",
            "stdout_part": "",
            "stderr_part": "end mismatch"}, "video/mpeg"),
        ("invalid_2_empty.m2v", {
            "purpose": "Test empty MPEG-2.",
            "stdout_part": "",
            "stderr_part": "Invalid data found when processing input"},
         "video/mpeg"),
        ("invalid__h264_aac_missing_data.mp4", {
            "purpose": "Test invalid MPEG-4.",
            "stdout_part": "",
            "stderr_part": "moov atom not found"}, "video/mp4"),
        ("invalid__empty.mp4", {
            "purpose": "Test invalid MPEG-4.",
            "stdout_part": "",
            "stderr_part": "Invalid data found when processing input"},
         "video/mp4"),
        ("invalid_1_missing_data.mp3", {
            "purpose": "Test invalid mp3.",
            "stdout_part": "",
            "stderr_part": "Header missing"}, "audio/mpeg"),
        ("invalid_1_wrong_version.mp3", {
            "purpose": "Test invalid mp3.",
            "stdout_part": "",
            "stderr_part": "Error while decoding stream"}, "audio/mpeg"),
        ("invalid__empty.mp3", {
            "purpose": "Test empty mp3",
            "stdout_part": "",
            "stderr_part": "could not find codec parameters"}, "audio/mpeg"),
        ("invalid__missing_data.ts", {
            "purpose": "Test invalid MPEG-TS.",
            "stdout_part": "",
            "stderr_part": "invalid new backstep"}, "video/MP2T"),
        ("invalid__empty.ts", {
            "purpose": "Test empty MPEG-TS.",
            "stdout_part": "",
            "stderr_part": "Invalid data found when processing input"},
         "video/MP2T"),
        ("invalid_1.2_jpeg2000_wrong_signature.mxf", {
            "purpose": "Test MXF with invalid header.",
            "stdout_part": "",
            "stderr_part": "Invalid data found when processing input"},
         "application/mxf"),
        ("invalid_1.2_jpeg2000_truncated.mxf", {
            "purpose": "Test truncated MXF.",
            "stdout_part": "",
            "stderr_part": "IndexSID 0 segment at 0 missing"},
         "application/mxf"),
        ("invalid__JPEG2000_no_avi_signature.avi", {
            "purpose": "Test AVI with invalid header.",
            "stdout_part": "",
            "stderr_part": "Error in analyzing file."},
         "video/avi"),
        ("invalid__JPEG2000_missing_data.avi", {
            "purpose": "Test truncated AVI.",
            "stdout_part": "",
            "stderr_part": "Invalid data found when processing input"},
         "video/avi"),
    ])
def test_ffmpeg_scraper_invalid(filename, result_dict, mimetype,
                                evaluate_scraper):
    """
    Test FFMpegScraper with invalid files.

    :filename: Test file name
    :result_dict: Result dict containing test purpose, and parts of
                  expected results of stdout and stderr
    :mimetype: Given and expected mimetype
    """
    correct = parse_results(filename, mimetype, result_dict, True)
    correct.streams = {}

    scraper = FFMpegScraper(filename=correct.filename,
                            mimetype="audio/mpeg")
    scraper.scrape_file()

    evaluate_scraper(scraper, correct)


@pytest.mark.parametrize(
    ["mime", "ver"],
    [
        ("video/mpeg", "1"),
        ("video/mp4", ""),
        ("video/MP1S", ""),
        ("video/MP2P", ""),
        ("video/MP2T", ""),
        ("video/avi", "")
    ]
)
def test_is_supported_mpeg(mime, ver):
    """
    Test is_supported method.

    :mime: Predefined mimetype
    :ver: Predefined version
    """
    assert FFMpegScraper.is_supported(mime, ver, True)
    assert FFMpegScraper.is_supported(mime, None, True)
    assert FFMpegScraper.is_supported(mime, ver, False)
    assert FFMpegScraper.is_supported(mime, "foo", True)
    assert not FFMpegScraper.is_supported("foo", ver, True)
