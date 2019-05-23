"""
Test module for ffmpeg.py

This module tests that:
    - For valid audio and video files the scraping is reported as successful,
      the file is well-formed. Since this scraper does not really collect
      metadata, the version and MIME type will be '(:unav)'.
    - For empty files the results are similar but file is not well-formed
      and errors should contain an error message. The error message should
      contain the following string:
        - With video/x-matroska, video/mpeg, video/mp4, video/MP2T files:
          'Invalid data found when processing input'.
        - With audio/mpeg files: 'could not find codec parameters'
        - With video/dv files: 'Cannot find DV header'
    - For invalid files the file is not well-formed and errors should contain
      an error message. With the files with missing data the error message
      should contain the following string:
        - With video/x-matroska files: 'Truncating packet of size'
        - With video/mpeg and video/mp4 files: 'end mismatch'
        - With video/MP2T files: 'invalid new backstep'
        - With audio/mpeg files: 'Error while decoding stream'
        - With video/dv files: 'AC EOB marker is absent'
    - For mp3 files with wrong version reported in the header, the file is not
      well-formed and errors should contain 'Error while decoding stream'.
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
        - video/mpeg, '1' or None
        - video/mp4, '' or None
        - video/MP1S, '' or None
        - video/MP2P, '' or None
        - video/MP2T, '' or None
    - When well-formedness is not checked, the scraper reports valid
      combinations as not supported.
    - A made up version with supported MIME type is reported as supported.
    - A made up MIME type with supported version is reported as not supported.
"""
import pytest
from file_scraper.ffmpeg.ffmpeg_scraper import FFMpegScraper
from tests.common import parse_results


@pytest.mark.parametrize(
    ["filename", "result_dict", "mimetype"],
    [
        ("valid__dv_wav.mov", {
            "purpose": "Test valid MOV with DV and WAV.",
            "stdout_part": "file was analyzed successfully",
            "stderr_part": ""}, "video/quicktime"),
        ("valid.dv", {
            "purpose": "Test valid DV.",
            "stdout_part": "file was analyzed successfully",
            "stderr_part": ""}, "video/dv"),
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
    ])
def test_ffmpeg_scraper_mov(filename, result_dict, mimetype,
                            evaluate_scraper):
    """Test FFMpegScraper."""
    correct = parse_results(filename, mimetype, result_dict, True)
    scraper = FFMpegScraper(correct.filename, True)
    scraper.scrape_file()
    correct.streams[0]["mimetype"] = "(:unav)"
    correct.streams[0]["version"] = "(:unav)"
    correct.streams[0]["stream_type"] = "videocontainer"

    if "invalid" in filename:
        correct.streams = {}

    evaluate_scraper(scraper, correct)


@pytest.mark.parametrize(
    ["filename", "result_dict"],
    [
        ("valid_4_ffv1.mkv", {
            "purpose": "Test valid MKV.",
            "stdout_part": "file was analyzed successfully",
            "stderr_part": ""}),
        ("invalid_4_ffv1_missing_data.mkv", {
            "purpose": "Test truncated MKV.",
            "stdout_part": "",
            "stderr_part": "Truncating packet of size"}),
        ("invalid__empty.mkv", {
            "purpose": "Test empty MKV.",
            "stdout_part": "",
            "stderr_part": "Invalid data found when processing input"}),
    ])
def test_ffmpeg_scraper_mkv(filename, result_dict, evaluate_scraper):
    """Test FFMpegScraper."""
    mimetype = "video/x-matroska"
    correct = parse_results(filename, mimetype, result_dict, True)
    scraper = FFMpegScraper(correct.filename, True)
    scraper.scrape_file()
    correct.streams[0]["mimetype"] = "(:unav)"
    correct.streams[0]["version"] = "(:unav)"
    correct.streams[0]["stream_type"] = "videocontainer"

    if "invalid" in filename:
        correct.streams = {}

    evaluate_scraper(scraper, correct)


@pytest.mark.parametrize(
    ["filename", "result_dict"],
    [
        ("valid_1.m1v", {
            "purpose": "Test valid MPEG-1.",
            "stdout_part": "file was analyzed successfully",
            "stderr_part": ""}),
        ("valid_2.m2v", {
            "purpose": "Test valid MPEG-2.",
            "stdout_part": "file was analyzed successfully",
            "stderr_part": ""}),
        ("invalid_1_missing_data.m1v", {
            "purpose": "Test invalid MPEG-1.",
            "stdout_part": "",
            "stderr_part": "end mismatch"}),
        ("invalid_1_empty.m1v", {
            "purpose": "Test empty MPEG-1.",
            "stdout_part": "",
            "stderr_part": "Invalid data found when processing input"}),
        ("invalid_2_missing_data.m2v", {
            "purpose": "Test invalid MPEG-2.",
            "stdout_part": "",
            "stderr_part": "end mismatch"}),
        ("invalid_2_empty.m2v", {
            "purpose": "Test empty MPEG-2.",
            "stdout_part": "",
            "stderr_part": "Invalid data found when processing input"})
    ])
def test_ffmpeg_scraper_mpeg(filename, result_dict, evaluate_scraper):
    """Test FFMpegScraper."""
    mimetype = "video/mpeg"
    correct = parse_results(filename, mimetype, result_dict, True)
    scraper = FFMpegScraper(correct.filename, True)
    scraper.scrape_file()
    correct.streams[0]["mimetype"] = "(:unav)"
    correct.streams[0]["version"] = "(:unav)"
    correct.streams[0]["stream_type"] = "videocontainer"

    if "invalid" in filename:
        correct.streams = {}

    evaluate_scraper(scraper, correct)


@pytest.mark.parametrize(
    ["filename", "result_dict"],
    [
        ("valid__h264_aac.mp4", {
            "purpose": "Test valid mp4.",
            "stdout_part": "file was analyzed successfully",
            "stderr_part": ""}),
        ("invalid__h264_aac_missing_data.mp4", {
            "purpose": "Test invalid MPEG-4.",
            "stdout_part": "",
            "stderr_part": "moov atom not found"}),
        ("invalid__empty.mp4", {
            "purpose": "Test invalid MPEG-4.",
            "stdout_part": "",
            "stderr_part": "Invalid data found when processing input"})
    ])
def test_ffmpeg_scraper_mp4(filename, result_dict, evaluate_scraper):
    """Test FFMpegScraper."""
    mimetype = "video/mp4"
    correct = parse_results(filename, mimetype, result_dict, True)
    scraper = FFMpegScraper(correct.filename, True)
    scraper.scrape_file()
    correct.streams[0]["mimetype"] = "(:unav)"
    correct.streams[0]["version"] = "(:unav)"
    correct.streams[0]["stream_type"] = "videocontainer"

    if "invalid" in filename:
        correct.streams = {}

    evaluate_scraper(scraper, correct)


@pytest.mark.parametrize(
    ["filename", "result_dict"],
    [
        ("valid_1.mp3", {
            "purpose": "Test valid mp3.",
            "stdout_part": "file was analyzed successfully",
            "stderr_part": ""}),
        ("invalid_1_missing_data.mp3", {
            "purpose": "Test invalid mp3.",
            "stdout_part": "",
            "stderr_part": "Header missing"}),
        ("invalid_1_wrong_version.mp3", {
            "purpose": "Test invalid mp3.",
            "stdout_part": "",
            "stderr_part": "Error while decoding stream"}),
        ("invalid__empty.mp3", {
            "purpose": "Test empty mp3",
            "stdout_part": "",
            "stderr_part": "could not find codec parameters"})
    ])
def test_ffmpeg_scraper_mp3(filename, result_dict, evaluate_scraper):
    """Test FFMpegScraper."""
    mimetype = "audio/mpeg"
    correct = parse_results(filename, mimetype, result_dict, True)
    scraper = FFMpegScraper(correct.filename, True)
    scraper.scrape_file()
    correct.version = None
    correct.streams[0]["mimetype"] = "(:unav)"
    correct.streams[0]["version"] = "(:unav)"
    correct.streams[0]["stream_type"] = "audio"

    if "invalid" in filename:
        correct.streams = {}

    evaluate_scraper(scraper, correct)


@pytest.mark.parametrize(
    ["filename", "result_dict"],
    [
        ("valid_.ts", {
            "purpose": "Test valid MPEG-TS.",
            "stdout_part": "file was analyzed successfully",
            "stderr_part": ""}),
        ("invalid__missing_data.ts", {
            "purpose": "Test invalid MPEG-TS.",
            "stdout_part": "",
            "stderr_part": "invalid new backstep"}),
        ("invalid__empty.ts", {
            "purpose": "Test empty MPEG-TS.",
            "stdout_part": "",
            "stderr_part": "Invalid data found when processing input"})
    ])
def test_ffmpeg_scraper_mpegts(filename, result_dict, evaluate_scraper):
    """Test FFMpegScraper."""
    mimetype = "video/MP2T"
    correct = parse_results(filename, mimetype, result_dict, True)
    scraper = FFMpegScraper(correct.filename, True)
    scraper.scrape_file()
    correct.version = None
    correct.streams[0]["mimetype"] = "(:unav)"
    correct.streams[0]["version"] = "(:unav)"
    correct.streams[0]["stream_type"] = "videocontainer"

    if "invalid" in filename:
        correct.streams = {}

    evaluate_scraper(scraper, correct)


#def test_no_wellformed():
#    """Test scraper without well-formed check."""
#    scraper = FFMpegScraper("tests/data/video_mpeg/valid_1.m1v", False)
#    scraper.scrape_file()
#    assert "Skipping scraper" in scraper.messages()
#    assert scraper.well_formed is None


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
