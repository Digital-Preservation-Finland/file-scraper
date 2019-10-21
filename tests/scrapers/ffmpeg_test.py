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
    - Otherwise supported MIME type is not supported when well-formedness is
      not checked.
    - If scraping is done without well-formedness check, an error is recorded
      and no metadata is scraped.
    - Forcing MIME type and/or version works.
"""
from __future__ import unicode_literals

import pytest

from file_scraper.ffmpeg.ffmpeg_scraper import FFMpegScraper
from tests.common import (parse_results, force_correct_filetype,
                          partial_message_included)
from tests.scrapers.stream_dicts import (
    AVI_CONTAINER,
    AVI_JPEG2000_VIDEO,
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
    """Test FFMpegScraper with valid files when no metadata is scraped."""
    correct = parse_results(filename, mimetype, result_dict, True)
    correct.streams.update(NO_METADATA)

    scraper = FFMpegScraper(correct.filename, True,
                            params={"mimetype_guess": mimetype})
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
        ("valid__JPEG2000_lossless.avi", {
            "purpose": "Test valid AVI with lossless JPEG2000.",
            "stdout_part": "file was analyzed successfully",
            "stderr_part": "",
            "streams": {0: AVI_CONTAINER.copy(),
                        1: dict(AVI_JPEG2000_VIDEO.copy(),
                                **{"data_rate": "3.559952"})}},
         "video/avi"),
# TODO enable this
#        ("valid_1.2_jpeg2000.mxf", {
#            "purpose": "Test valid MXF.",
#            "stdout_part": "file was analyzed successfully",
#            "stderr_part": ""},
#         "application/mxf"),
    ])
def test_ffmpeg_scraper_valid(filename, result_dict, mimetype,
                              evaluate_scraper):
    """Test FFMpegScraper with valid files when metadata is scraped."""
    correct = parse_results(filename, mimetype, result_dict, True)

    scraper = FFMpegScraper(correct.filename, True,
                            params={"mimetype_guess": mimetype})
    scraper.scrape_file()
    # TODO remove these when mxf testing is added and made functional
#    from file_scraper.utils import generate_metadata_dict
#    print generate_metadata_dict([scraper.streams], [])
#    for stream in range(len(scraper.streams)):
#        print "scraper: " + scraper.streams[stream].stream_type()
#        print "correct: " + correct.streams[stream]["stream_type"]

    evaluate_scraper(scraper, correct)


def test_no_wellformed():
    """
    Test that scraping is also done without well-formedness check.
    """
    scraper = FFMpegScraper("tests/data/video_avi/valid__JPEG2000.avi", False,
                            {"mimetype_guess": "video/avi"})
    scraper.scrape_file()
    assert partial_message_included("The file was analyzed successfully.",
                                    scraper.messages())
    assert scraper.well_formed is None


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
    ])
def test_ffmpeg_scraper_invalid(filename, result_dict, mimetype,
                                evaluate_scraper):
    """Test FFMpegScraper with invalid files."""
    correct = parse_results(filename, mimetype, result_dict, True)
    correct.streams = {}

    scraper = FFMpegScraper(correct.filename, True,
                            {"mimetype_guess": "audio/mpeg"})
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
    """Test is_supported method."""
    assert FFMpegScraper.is_supported(mime, ver, True)
    assert FFMpegScraper.is_supported(mime, None, True)
    assert FFMpegScraper.is_supported(mime, ver, False)
    assert FFMpegScraper.is_supported(mime, "foo", True)
    assert not FFMpegScraper.is_supported("foo", ver, True)


@pytest.mark.parametrize(
    ["filename", "result_dict", "filetype"],
    [
        ("valid_4_ffv1.mkv", {
            "purpose": "Test not forcing either MIME type or version",
            "stdout_part": "The file was analyzed successfully",
            "stderr_part": ""},
         {"given_mimetype": None, "given_version": None,
          "expected_mimetype": "video/x-matroska",
          "expected_version": "(:unav)",
          "correct_mimetype": "video/x-matroska"}),
        ("valid_4_ffv1.mkv", {
            "purpose": "Test forcing a supported MIME type",
            "stdout_part": "MIME type not scraped",
            "stderr_part": ""},
         {"given_mimetype": "other/mimetype", "given_version": None,
          "expected_mimetype": "other/mimetype",
          "expected_version": "(:unav)",
          "correct_mimetype": "video/x-matroska"}),
        ("valid_4_ffv1.mkv", {
            "purpose": "Test forcing a supported MIME type and version",
            "stdout_part": "MIME type and version not scraped",
            "stderr_part": ""},
         {"given_mimetype": "video/x-matroska", "given_version": "4",
          "expected_mimetype": "video/x-matroska", "expected_version": "4",
          "correct_mimetype": "video/x-matroska"}),
         # TODO enable test when there's support
#        ("valid_4_ffv1.mkv", {
#            "purpose": "Test forcing unsupported MIME type",
#            "stdout_part": "MIME type not scraped",
#            "stderr_part": "is not supported"},
#         {"given_mimetype": "custom/mime", "given_version": None,
#          "expected_mimetype": "custom/mime", "expected_version": "(:unav)",
#          "correct_mimetype": "video/x-matroska"}),
        ("valid_4_ffv1.mkv", {
            "purpose": "Test forcing MIME type and version",
            "stdout_part": "MIME type and version not scraped",
            "stderr_part": ""},
         {"given_mimetype": "custom/mime", "given_version": "99.9",
          "expected_mimetype": "custom/mime", "expected_version": "99.9",
          "correct_mimetype": "video/x-matroska"}),
        ("valid_4_ffv1.mkv", {
            "purpose": "Test forcing version (should have no effect)",
            "stdout_part": "The file was analyzed successfully",
            "stderr_part": ""},
         {"given_mimetype": None, "given_version": "99.9",
          "expected_mimetype": "video/x-matroska",
          "expected_version": "(:unav)",
          "correct_mimetype": "video/x-matroska"}),
    ]
)
def test_forcing_filetype(filename, result_dict, filetype, evaluate_scraper):
    """Test forcing scraper to use a given MIME type and/or version."""
    correct = force_correct_filetype(filename, result_dict, filetype)
    if correct.streams:
        correct.streams[0]["stream_type"] = "(:unav)"

    params = {"mimetype": filetype["given_mimetype"],
              "version": filetype["given_version"],
              "mimetype_guess": filetype["correct_mimetype"]}
    scraper = FFMpegScraper(correct.filename, True, params)
    scraper.scrape_file()

    evaluate_scraper(scraper, correct)
