"""
Test module for ffmpeg.py

This module tests that:
    - For valid audio and video files the scraping is reported as successful,
      the file is well-formed. Since this scraper does not really collect
      metadata, the version and MIME type will be "(:unav)".
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
    - When well-formed check is performed, the scraper reports the following
      combinations of mimetypes and versions as supported:
        - video/mpeg, "1" or None
        - video/mp4, "" or None
        - video/MP1S, "" or None
        - video/MP2P, "" or None
        - video/MP2T, "" or None
    - When well-formedness is not checked, the scraper reports valid
      combinations as not supported.
    - A made up version with supported MIME type is reported as supported.
    - A made up MIME type with supported version is reported as not supported.
"""
import pytest
from file_scraper.ffmpeg.ffmpeg_scraper import FFMpegScraper
from tests.common import parse_results

from file_scraper.utils import generate_metadata_dict # TODO remove


@pytest.mark.parametrize(
    ["filename", "result_dict", "mimetype"],
    [
        ("valid__dv_wav.mov", {
            "purpose": "Test valid MOV with DV and WAV.",
            "stdout_part": "file was analyzed successfully",
            "stderr_part": "",
            "streams": {
                0: {
                    "index": 0,
                    "stream_type": "videocontainer"},
                1: {
                    "index": 1,
                    "par": "1.422",
                    "frame_rate": u"25",
                    "data_rate_mode": None,
                    "color": "Color",
                    "codec_quality": None,
                    "dar": "1.778",
                    "height": "576",
                    "sound": "Yes",
                    "codec_name": "DV",
                    "sampling": "4:2:0",
                    "stream_type": u"video",
                    "width": "720"},
                2: {
                    "index": 2,
                    "audio_data_encoding": u"PCM",
                    "data_rate_mode": None,
                    "codec_quality": None,
                    "stream_type": u"audio",
                    "sampling_frequency": "44.1",
                    "num_channels": "2",
                    "codec_name": "PCM",
                    "data_rate": "705.6"},
                3: {"index": 3,
                    "stream_type": "other"}}},
         "video/quicktime"),
        ("valid.dv", {
            "purpose": "Test valid DV.",
            "stdout_part": "file was analyzed successfully",
            "stderr_part": "",
            "streams": {
                0: {
                    "index": 0,
                    "stream_type": "videocontainer"},
                1: {
                    "index": 1,
                    "par": "1.422",
                    "frame_rate": u"25",
                    "data_rate_mode": None,
                    "color": "Color",
                    "codec_quality": None,
                    "dar": "1.778",
                    "height": "576",
                    "sound": "No",
                    "codec_name": "DV",
                    "sampling": "4:2:0",
                    "stream_type": u"video",
                    "width": "720"}}},
         "video/dv"),
        ("valid_4_ffv1.mkv", {
            "purpose": "Test valid MKV.",
            "stdout_part": "file was analyzed successfully",
            "stderr_part": "",
            "streams": {
                0: {
                    "index": 0,
                    "stream_type": "videocontainer"},
                1: {
                    "index": 1,
                    "par": "1",
                    "frame_rate": u"30",
                    "bits_per_sample": "8",
                    "data_rate_mode": None,
                    "color": "Color",
                    "codec_quality": None,
                    "dar": "1.778",
                    "height": "180",
                    "sound": "No",
                    "codec_name": "FFV1",
                    "sampling": "4:2:0",
                    "stream_type": u"video",
                    "width": "320"}}},
         "video/x-matroska"),
        ("valid_1.m1v", {
            "purpose": "Test valid MPEG-1.",
            "stdout_part": "file was analyzed successfully",
            "stderr_part": "",
            "streams": {
                0: {
                    "index": 0,
                    "stream_type": "videocontainer"},
                1: {
                    "index": 1,
                    "par": "1",
                    "frame_rate": u"30",
                    "data_rate_mode": None,
                    "color": "Color",
                    "codec_quality": None,
                    "dar": "1.778",
                    "height": "180",
                    "sound": "No",
                    "codec_name": "MPEG Video",
                    "sampling": "4:2:0",
                    "stream_type": u"video",
                    "width": "320"}}}, "video/mpeg"),
        ("valid_2.m2v", {
            "purpose": "Test valid MPEG-2.",
            "stdout_part": "file was analyzed successfully",
            "stderr_part": "",
            "streams": {
                0: {
                    "index": 0,
                    "stream_type": "videocontainer"},
                1: {
                    "index": 1,
                    "par": "1",
                    "frame_rate": u"30",
                    "data_rate_mode": None,
                    "color": "Color",
                    "codec_quality": None,
                    "dar": "1.778",
                    "height": "180",
                    "sound": "No",
                    "codec_name": "MPEG Video",
                    "sampling": "4:2:0",
                    "stream_type": u"video",
                    "width": "320"}}}, "video/mpeg"),
        ("valid__h264_aac.mp4", {
            "purpose": "Test valid mp4.",
            "stdout_part": "file was analyzed successfully",
            "stderr_part": "",
            "streams": {
                0: {
                    "index": 0,
                    "stream_type": "videocontainer"},
                1: {
                    "index": 1,
                    "par": "1",
                    "frame_rate": u"30",
                    "bits_per_sample": "8",
                    "data_rate_mode": None,
                    "color": "Color",
                    "codec_quality": None,
                    "dar": "1.778",
                    "height": "180",
                    "sound": "Yes",
                    "sampling": "4:2:0",
                    "stream_type": u"video",
                    "width": "320"},
                2: {
                    "index": 2,
                    "audio_data_encoding": u"AAC",
                    "data_rate_mode": None,
                    "codec_quality": None,
                    "stream_type": u"audio",
                    "sampling_frequency": "44.1",
                    "num_channels": "2",
                    "codec_name": "AAC",
                    "data_rate": "135.233"}}}, "video/mp4"),
        ("valid_1.mp3", {
            "purpose": "Test valid mp3.",
            "stdout_part": "file was analyzed successfully",
            "stderr_part": "",
            "streams": {
                0: {
                    "index": 0,
                    "data_rate_mode": None,
                    "codec_quality": None,
                    "stream_type": "audio"},
                1: {
                    "index": 1,
                    "audio_data_encoding": "MPEG Audio",
                    "data_rate_mode": None,
                    "codec_quality": None,
                    "stream_type": u"audio",
                    "sampling_frequency": "44.1",
                    "num_channels": "2",
                    "codec_name": "MPEG Audio",
                    "data_rate": "128"}}}, "audio/mpeg"),
        ("valid_.ts", {
            "purpose": "Test valid MPEG-TS.",
            "stdout_part": "file was analyzed successfully",
            "stderr_part": "",
            "streams": {
                0: {
                    "index": 0,
                    "stream_type": "videocontainer"},
                1: {
                    "index": 1,
                    "par": "1",
                    "frame_rate": u"30",
                    "data_rate_mode": None,
                    "color": "Color",
                    "codec_quality": None,
                    "dar": "1.778",
                    "height": "180",
                    "sound": "Yes",
                    "codec_name": "MPEG Video",
                    "sampling": "4:2:0",
                    "stream_type": u"video",
                    "width": "320"},
                2: {
                    "index": 2,
                    "audio_data_encoding": "MPEG Audio",
                    "data_rate_mode": None,
                    "codec_quality": None,
                    "stream_type": u"audio",
                    "sampling_frequency": "44.1",
                    "num_channels": "2",
                    "codec_name": "MPEG Audio",
                    "data_rate": "128"}}}, "video/MP2T"),
    ])
def test_ffmpeg_scraper_valid(filename, result_dict, mimetype,
                              evaluate_scraper):
    """Test FFMpegScraper with valid files."""
    for check_well_formed in [True, False]:
        correct = parse_results(filename, mimetype, result_dict,
                                check_well_formed)
        correct.streams[0]["mimetype"] = "(:unav)"
        correct.streams[0]["version"] = "(:unav)"
        if "audio" in mimetype:
            correct.streams[0]["stream_type"] = "audio"
        else:
            correct.streams[0]["stream_type"] = "videocontainer"
        if not check_well_formed:
            correct.well_formed = None

        scraper = FFMpegScraper(correct.filename, check_well_formed)
        scraper.scrape_file()
        print generate_metadata_dict([scraper.streams], [])
        assert len(correct.streams) > 1

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
         "video/MP2T")
    ])
def test_ffmpeg_scraper_invalid(filename, result_dict, mimetype,
                                evaluate_scraper):
    """Test FFMpegScraper with invalid files."""
    for check_well_formed in [True, False]:
        correct = parse_results(filename, mimetype, result_dict,
                                check_well_formed)
        correct.streams = {}

        scraper = FFMpegScraper(correct.filename, check_well_formed)
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
    ]
)
def test_is_supported_mpeg(mime, ver):
    """Test is_supported method."""
    assert FFMpegScraper.is_supported(mime, ver, True)
    assert FFMpegScraper.is_supported(mime, None, True)
    assert FFMpegScraper.is_supported(mime, ver, False)
    assert FFMpegScraper.is_supported(mime, "foo", True)
    assert not FFMpegScraper.is_supported("foo", ver, True)
