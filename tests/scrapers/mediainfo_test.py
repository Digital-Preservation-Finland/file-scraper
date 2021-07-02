"""
Test module for Mediainfo.

NOTE: Mediainfo accepts practically any file. We use another scrapers
for well-formed checks.

This module tests that:
    - MIME type, version, streams, and well-formedness are scraped
      correctly for dv, wav, m1v, m2v, mp4, mp3 and ts files.
      Additionally, this is scraped correctly to mov video container
      containing dv video and lpcm8 audio, and to mkv container
      containing ffv1 video without sound and with lpcm8 and flac sound.
      For valid files scraper messages contains 'file was analyzed
      successfully' and for empty file scraper errors contains 'No audio
      or video tracks found'.
    - The following MIME type and version combinations are supported
      whether well-formedness is checked or not:
        - audio/x-wav, '2'
        - video/mpeg, '1'
        - video/mp4, ''
        - video/MP1S, ''
        - video/MP2P, ''
        - video/MP2T, ''
    - These MIME types are also supported with a made up version.
    - Made up MIME types are not supported.
"""
from __future__ import unicode_literals

import pytest

from file_scraper.defaults import UNAP
from file_scraper.mediainfo.mediainfo_scraper import MediainfoScraper
from tests.common import (parse_results, partial_message_included)
from tests.scrapers.stream_dicts import (DV_VIDEO,
                                         FFV_VIDEO,
                                         FFV_VIDEO_TRUNCATED,
                                         FFV_VIDEO_SOUND,
                                         FFV_VIDEO_SOUND_DATARATE,
                                         FLAC_AUDIO,
                                         MKV_CONTAINER,
                                         MOV_CONTAINER,
                                         MOV_DV_VIDEO,
                                         MOV_MPEG4_VIDEO,
                                         MOV_MPEG4_AUDIO,
                                         MPEG1_AUDIO,
                                         MPEG1_VIDEO,
                                         MPEG2_VIDEO,
                                         MPEG4_AUDIO,
                                         MPEG4_CONTAINER,
                                         MPEG4_VIDEO,
                                         MPEGTS_AUDIO,
                                         MPEGTS_CONTAINER,
                                         MPEGTS_VIDEO,
                                         LPCM8_AUDIO,
                                         WAV_AUDIO,
                                         AVI_CONTAINER,
                                         AVI_VIDEO,
                                         AVI_AUDIO)


@pytest.mark.parametrize(
    ["filename", "result_dict", "mimetype"],
    [
        ("valid__dv_lpcm8.mov", {
            "purpose": "Test valid MOV with DV and LPCM8.",
            "stdout_part": "file was analyzed successfully",
            "stderr_part": "",
            "streams": {0: MOV_CONTAINER.copy(),
                        1: MOV_DV_VIDEO.copy(),
                        2: LPCM8_AUDIO.copy()}},
         "video/quicktime"),
        ("valid__h264_aac.mov", {
            "purpose": "Test valid MOV with AVC and AAC.",
            "stdout_part": "file was analyzed successfully",
            "stderr_part": "",
            "streams": {0: MOV_CONTAINER.copy(),
                        1: MOV_MPEG4_VIDEO.copy(),
                        2: MOV_MPEG4_AUDIO.copy()}},
         "video/quicktime"),
        ("valid__pal_lossy.dv", {
            "purpose": "Test valid DV.",
            "stdout_part": "file was analyzed successfully",
            "stderr_part": "",
            "streams": {0: DV_VIDEO.copy()}},
         "video/dv"),
        ("invalid__empty.dv", {
            "purpose": "Test empty DV.",
            "stdout_part": "",
            "stderr_part": "No audio or video tracks found"},
         "video/dv"),
    ])
def test_mediainfo_scraper_mov(filename, result_dict, mimetype,
                               evaluate_scraper):
    """
    Test Quicktime and DV scraping with Mediainfo.

    :filename: Test file name
    :result_dict: Result dict containing the test purpose, parts of
                  expected results of stdout and stderr, and expected
                  streams
    :mimetype: File MIME type
    """
    correct = parse_results(filename, mimetype, result_dict, True)
    scraper = MediainfoScraper(filename=correct.filename, mimetype=mimetype)
    scraper.scrape_file()

    if ".dv" in filename:
        correct.streams[0].pop("stream_type", None)

    if "empty" in filename:
        assert partial_message_included(correct.stdout_part,
                                        scraper.messages())
        assert partial_message_included(correct.stderr_part, scraper.errors())
        assert not scraper.streams
    else:
        evaluate_scraper(scraper, correct)


@pytest.mark.parametrize(
    ["filename", "result_dict"],
    [
        ("valid_4_ffv1.mkv", {
            "purpose": "Test valid MKV.",
            "stdout_part": "file was analyzed successfully",
            "stderr_part": "",
            "streams": {0: MKV_CONTAINER.copy(),
                        1: FFV_VIDEO.copy()}}),
        ("valid_4_ffv1_flac.mkv", {
            "purpose": "Test valid MKV wit FFV1 and FLAC stream",
            "stdout_part": "file was analyzed successfully",
            "stderr_part": "",
            "streams": {0: MKV_CONTAINER.copy(),
                        1: FFV_VIDEO_SOUND.copy(),
                        2: FLAC_AUDIO.copy()}}),
        ("valid_4_ffv1_lpcm8.mkv", {
            "purpose": "Test valid MKV with FFV1 and LPCM8.",
            "stdout_part": "file was analyzed successfully",
            "stderr_part": "",
            "streams": {0: MKV_CONTAINER.copy(),
                        1: FFV_VIDEO_SOUND_DATARATE.copy(),
                        2: LPCM8_AUDIO.copy()}}),
        ("invalid_4_ffv1_missing_data.mkv", {
            "purpose": "Test truncated MKV.",
            "stdout_part": "",
            "stderr_part": "The file is truncated.",
            "streams": {0: MKV_CONTAINER.copy(),
                        1: FFV_VIDEO_TRUNCATED.copy()}}),
        ("invalid__empty.mkv", {
            "purpose": "Test empty MKV.",
            "stdout_part": "",
            "stderr_part": "No audio or video tracks found"}),
    ])
def test_mediainfo_scraper_mkv(filename, result_dict, evaluate_scraper):
    """
    Test Matroska scraping with Mediainfo.

    :filename: Test file name
    :result_dict: Result dict containing the test purpose, parts of
                  expected results of stdout and stderr, and expected
                  streams
    """
    mimetype = "video/x-matroska"
    correct = parse_results(filename, mimetype, result_dict, True)
    scraper = MediainfoScraper(filename=correct.filename, mimetype=mimetype)
    scraper.scrape_file()
    if "empty" in filename:
        correct.version = None
        correct.streams[0]["version"] = None
        correct.streams[0]["stream_type"] = None

    if "invalid" in filename:
        assert partial_message_included(correct.stdout_part,
                                        scraper.messages())
        assert partial_message_included(correct.stderr_part, scraper.errors())
        assert not scraper.streams
    else:
        evaluate_scraper(scraper, correct)


@pytest.mark.parametrize(
    ["filename", "result_dict"],
    [
        ("valid__wav.wav", {
            "purpose": "Test valid WAV.",
            "stdout_part": "file was analyzed successfully",
            "stderr_part": "",
            "streams": {0: WAV_AUDIO.copy()}}),
        ("valid_2_bwf.wav", {
            "purpose": "Test valid BWF.",
            "stdout_part": "file was analyzed successfully",
            "stderr_part": "",
            "streams": {0: WAV_AUDIO.copy()}}),
        ("invalid__empty.wav", {
            "purpose": "Test empty WAV.",
            "stdout_part": "",
            "stderr_part": "No audio or video tracks found"}),
    ])
def test_mediainfo_scraper_wav(filename, result_dict, evaluate_scraper):
    """
    Test WAV scraping with Mediainfo.

    :filename: Test file name
    :result_dict: Result dict containing the test purpose, parts of
                  expected results of stdout and stderr, and expected
                  streams
    """
    mimetype = "audio/x-wav"
    correct = parse_results(filename, mimetype, result_dict, True)
    if "2" in filename:
        correct.streams[0]["version"] = "2"
    else:
        correct.streams[0]["version"] = UNAP

    scraper = MediainfoScraper(filename=correct.filename, mimetype=mimetype)
    scraper.scrape_file()

    if "empty" in filename:
        assert partial_message_included(correct.stdout_part,
                                        scraper.messages())
        assert partial_message_included(correct.stderr_part, scraper.errors())
        assert not scraper.streams
    else:
        evaluate_scraper(scraper, correct)


@pytest.mark.parametrize(
    ["filename", "result_dict"],
    [
        ("valid_1.m1v", {
            "purpose": "Test valid MPEG-1.",
            "stdout_part": "file was analyzed successfully",
            "stderr_part": "",
            "streams": {0: MPEG1_VIDEO.copy()}}),
        ("valid_2.m2v", {
            "purpose": "Test valid MPEG-2.",
            "stdout_part": "file was analyzed successfully",
            "stderr_part": "",
            "streams": {0: MPEG2_VIDEO.copy()}}),
        ("invalid_1_empty.m1v", {
            "purpose": "Test empty MPEG-1.",
            "stdout_part": "",
            "stderr_part": "No audio or video tracks found"}),
        ("invalid_2_empty.m2v", {
            "purpose": "Test empty MPEG-2.",
            "stdout_part": "",
            "stderr_part": "No audio or video tracks found"})
    ])
def test_mediainfo_scraper_mpeg(filename, result_dict, evaluate_scraper):
    """
    Test MPEG scraping with MediainfoScraper.

    :filename: Test file name
    :result_dict: Result dict containing the test purpose, parts of
                  expected results of stdout and stderr, and expected
                  streams
    """
    mimetype = "video/mpeg"
    correct = parse_results(filename, mimetype, result_dict, True)
    scraper = MediainfoScraper(filename=correct.filename, mimetype=mimetype)
    scraper.scrape_file()
    if "empty" in filename:
        assert partial_message_included(correct.stdout_part,
                                        scraper.messages())
        assert partial_message_included(correct.stderr_part, scraper.errors())
        assert not scraper.streams
    else:
        evaluate_scraper(scraper, correct)


@pytest.mark.parametrize(
    ["filename", "result_dict"],
    [
        (
            "valid__h264_aac.mp4",
            {
                "purpose": "Test valid mp4.",
                "stdout_part": "file was analyzed successfully",
                "stderr_part": "",
                "streams": {0: MPEG4_CONTAINER.copy(),
                            1: MPEG4_VIDEO.copy(),
                            2: MPEG4_AUDIO.copy()}
            }
        ),
        (
            "invalid__empty.mp4",
            {
                "purpose": "Test invalid MPEG-4.",
                "stdout_part": "",
                "stderr_part": "No audio or video tracks found"
            }
        )
    ]
)
def test_mediainfo_scraper_mp4(filename, result_dict, evaluate_scraper):
    """
    Test MP4 scraping with MediainfoScraper.

    :filename: Test file name
    :result_dict: Result dict containing the test purpose, parts of
                  expected results of stdout and stderr, and expected
                  streams
    """
    mimetype = "video/mp4"
    correct = parse_results(filename, mimetype, result_dict, True)
    scraper = MediainfoScraper(filename=correct.filename, mimetype=mimetype)
    scraper.scrape_file()

    if "empty" in filename:
        assert partial_message_included(correct.stdout_part,
                                        scraper.messages())
        assert partial_message_included(correct.stderr_part, scraper.errors())
        assert not scraper.streams
    else:
        evaluate_scraper(scraper, correct)


@pytest.mark.parametrize(
    ["filename", "result_dict"],
    [
        ("valid_1.mp3", {
            "purpose": "Test valid mp3.",
            "stdout_part": "file was analyzed successfully",
            "stderr_part": "",
            "streams": {0: MPEG1_AUDIO.copy()}}),
        ("invalid__empty.mp3", {
            "purpose": "Test empty mp3",
            "stdout_part": "",
            "stderr_part": "No audio or video tracks found"})
    ])
def test_mediainfo_scraper_mp3(filename, result_dict, evaluate_scraper):
    """
    Test MP3 scraping with MediainfoScraper.

    :filename: Test file name
    :result_dict: Result dict containing the test purpose, parts of
                  expected results of stdout and stderr, and expected
                  streams
    """
    mimetype = "audio/mpeg"
    correct = parse_results(filename, mimetype, result_dict, True)
    scraper = MediainfoScraper(filename=correct.filename, mimetype=mimetype)
    scraper.scrape_file()

    if "empty" in filename:
        assert partial_message_included(correct.stdout_part,
                                        scraper.messages())
        assert partial_message_included(correct.stderr_part, scraper.errors())
        assert not scraper.streams
    else:
        correct.streams[0].pop("stream_type", None)
        evaluate_scraper(scraper, correct)


@pytest.mark.parametrize(
    ["filename", "result_dict"],
    [
        (
            "valid__mpeg2_mp3.ts",
            {
                "purpose": "Test valid MPEG-TS.",
                "stdout_part": "file was analyzed successfully",
                "stderr_part": "",
                "streams": {0: MPEGTS_CONTAINER.copy(),
                            1: MPEGTS_VIDEO.copy(),
                            2: MPEGTS_AUDIO.copy()}
            }
        ),
        (
            "invalid__empty.ts",
            {
                "purpose": "Test empty MPEG-TS.",
                "stdout_part": "",
                "stderr_part": "No audio or video tracks found"
            }
        )
    ])
def test_mediainfo_scraper_mpegts(filename, result_dict, evaluate_scraper):
    """
    Test MPEG Transport Stream scraping with MediainfoScraper.

    :filename: Test file name
    :result_dict: Result dict containing the test purpose, parts of
                  expected results of stdout and stderr, and expected
                  streams
    """
    mimetype = "video/MP2T"
    correct = parse_results(filename, mimetype, result_dict, True)
    scraper = MediainfoScraper(filename=correct.filename, mimetype=mimetype)
    scraper.scrape_file()

    if "empty" in filename:
        assert partial_message_included(correct.stdout_part,
                                        scraper.messages())
        assert partial_message_included(correct.stderr_part, scraper.errors())
        assert not scraper.streams
    else:
        evaluate_scraper(scraper, correct)


def test_mediainfo_scraper_avi(evaluate_scraper):
    """Test AVI scraping with MediainfoScraper."""
    filename = "valid__mpeg2_mp3.avi"
    mimetype = "video/avi"
    result_dict = {
        "purpose": "Test valid AVI.",
        "stdout_part": "file was analyzed successfully",
        "stderr_part": "",
        "streams": {0: AVI_CONTAINER.copy(),
                    1: AVI_VIDEO.copy(),
                    2: AVI_AUDIO.copy()}
    }

    correct = parse_results(filename, mimetype, result_dict, True)
    scraper = MediainfoScraper(filename=correct.filename, mimetype=mimetype)
    scraper.scrape_file()

    evaluate_scraper(scraper, correct)


@pytest.mark.parametrize(
    ["mime", "ver"],
    [
        ("video/avi", ""),
        ("video/mpeg", "1"),
        ("video/mp4", ""),
        ("video/MP1S", ""),
        ("video/MP2P", ""),
        ("video/MP2T", ""),
        ("audio/x-wav", ""),
    ]
)
def test_is_supported(mime, ver):
    """
    Test is_supported method for different file types.

    AVI files are scraped using FFMpeg for easy colour information
    collection, but Mediainfo is also needed for checking
    well-formedness, so AVI should be supported.

    :mime: MIME type
    :ver: File format version
    """
    assert MediainfoScraper.is_supported(mime, ver, True)
    assert MediainfoScraper.is_supported(mime, None, True)
    assert MediainfoScraper.is_supported(mime, ver, False)
    assert MediainfoScraper.is_supported(mime, "foo", True)
    assert not MediainfoScraper.is_supported("foo", ver, True)
