"""
Test module for Mediainfo.

NOTE: Mediainfo accepts practically any file. We use another scrapers for
well-formed checks.

This module tests that:
    - MIME type, version, streams, and well-formedness are scraped correctly
      for dv, wav, m1v, m2v, mp4, mp3 and ts files. Additionally, this is
      scraped correctly to mov video container containing dv video and pcm
      (i.e. wav) audio, and to mkv container containing ffv1 video. For valid
      files scraper messages contains 'file was analyzed successfully' and for
      empty file scraper errors contains 'No audio or video tracks found'.
    - When well-formedness is not checked, scraper messages does NOT contain
      'Skipping scraper' (i.e. the metadata is collected anyway), but
      well_formed is None. This is tested with a wav file.
    - The following MIME type and version combinations are supported whether
      well-formedness is checked or not:
        - audio/x-wav, '2'
        - video/mpeg, '1'
        - video/mp4, ''
        - video/MP1S, ''
        - video/MP2P, ''
        - video/MP2T, ''
    - These MIME types are also supported with a made up version.
    - Made up MIME types are not supported.
    - Error is raised if mimetype_guess is not supplied.
    - MIME type and/or version forcing works.
"""
from __future__ import unicode_literals

import pytest
import six

from file_scraper.mediainfo.mediainfo_scraper import MediainfoScraper
from tests.common import parse_results, force_correct_filetype
from tests.scrapers.stream_dicts import (DV_VIDEO, FFV_VIDEO,
                                         FFV_VIDEO_TRUNCATED, MKV_CONTAINER,
                                         MOV_CONTAINER, MOV_DV_VIDEO, MOV_TC,
                                         MPEG1_AUDIO, MPEG1_VIDEO, MPEG2_VIDEO,
                                         MPEG4_AUDIO, MPEG4_CONTAINER,
                                         MPEG4_VIDEO, MPEGTS_AUDIO,
                                         MPEGTS_CONTAINER, MPEGTS_OTHER,
                                         MPEGTS_VIDEO, WAV_AUDIO)


@pytest.mark.parametrize(
    ["filename", "result_dict", "mimetype"],
    [
        ("valid__dv_wav.mov", {
            "purpose": "Test valid MOV with DV and WAV.",
            "stdout_part": "file was analyzed successfully",
            "stderr_part": "",
            "streams": {0: MOV_CONTAINER.copy(),
                        1: MOV_DV_VIDEO.copy(),
                        2: WAV_AUDIO.copy(),
                        3: MOV_TC.copy()}}, "video/quicktime"),
        ("valid.dv", {
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
    """Test Quicktime and DV scraping with Mediainfo."""
    correct = parse_results(filename, mimetype, result_dict, True)
    scraper = MediainfoScraper(correct.filename, True,
                               params={"mimetype_guess": mimetype})
    scraper.scrape_file()

    if ".dv" in filename:
        correct.streams[0].pop("stream_type", None)

    if "empty" in filename:
        assert correct.stdout_part in scraper.messages()
        assert correct.stderr_part in scraper.errors()
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
    """Test Matroska scraping with Mediainfo."""
    mimetype = "video/x-matroska"
    correct = parse_results(filename, mimetype, result_dict, True)
    scraper = MediainfoScraper(correct.filename, True,
                               params={"mimetype_guess": mimetype})
    scraper.scrape_file()
    if "empty" in filename:
        correct.version = None
        correct.streams[0]["version"] = None
        correct.streams[0]["stream_type"] = None

    if "empty" in filename:
        assert correct.stdout_part in scraper.messages()
        assert correct.stderr_part in scraper.errors()
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
    """Test WAV scraping with Mediainfo."""
    mimetype = "audio/x-wav"
    correct = parse_results(filename, mimetype, result_dict, True)
    scraper = MediainfoScraper(correct.filename, True,
                               params={"mimetype_guess": mimetype})
    scraper.scrape_file()

    if filename == "valid__wav.wav":
        correct.streams[0]["version"] = ""
    if "empty" in filename:
        assert correct.stdout_part in scraper.messages()
        assert correct.stderr_part in scraper.errors()
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
    """Test MPEG scraping with MediainfoScraper."""
    mimetype = "video/mpeg"
    correct = parse_results(filename, mimetype, result_dict, True)
    scraper = MediainfoScraper(correct.filename, True,
                               params={"mimetype_guess": mimetype})
    scraper.scrape_file()
    del correct.streams[0]["stream_type"]
    if "empty" in filename:
        assert correct.stdout_part in scraper.messages()
        assert correct.stderr_part in scraper.errors()
        assert not scraper.streams
    else:
        evaluate_scraper(scraper, correct)


@pytest.mark.parametrize(
    ["filename", "result_dict"],
    [
        ("valid__h264_aac.mp4", {
            "purpose": "Test valid mp4.",
            "stdout_part": "file was analyzed successfully",
            "stderr_part": "",
            "streams": {0: MPEG4_CONTAINER.copy(),
                        1: MPEG4_VIDEO.copy(),
                        2: MPEG4_AUDIO.copy()}}),
        ("invalid__empty.mp4", {
            "purpose": "Test invalid MPEG-4.",
            "stdout_part": "",
            "stderr_part": "No audio or video tracks found"})
    ])
def test_mediainfo_scraper_mp4(filename, result_dict, evaluate_scraper):
    """Test MP4 scraping with MediainfoScraper."""
    mimetype = "video/mp4"
    correct = parse_results(filename, mimetype, result_dict, True)
    scraper = MediainfoScraper(correct.filename, True,
                               params={"mimetype_guess": mimetype})
    scraper.scrape_file()

    for stream in correct.streams.values():
        stream["version"] = "(:unav)"
    if "empty" in filename:
        assert correct.stdout_part in scraper.messages()
        assert correct.stderr_part in scraper.errors()
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
    """Test MP3 scraping with MediainfoScraper."""
    mimetype = "audio/mpeg"
    correct = parse_results(filename, mimetype, result_dict, True)
    scraper = MediainfoScraper(correct.filename, True,
                               params={"mimetype_guess": mimetype})
    scraper.scrape_file()

    if "empty" in filename:
        assert correct.stdout_part in scraper.messages()
        assert correct.stderr_part in scraper.errors()
        assert not scraper.streams
    else:
        correct.streams[0].pop("stream_type", None)
        evaluate_scraper(scraper, correct)


@pytest.mark.parametrize(
    ["filename", "result_dict"],
    [
        ("valid_.ts", {
            "purpose": "Test valid MPEG-TS.",
            "stdout_part": "file was analyzed successfully",
            "stderr_part": "",
            "streams": {0: MPEGTS_CONTAINER.copy(),
                        1: MPEGTS_VIDEO.copy(),
                        2: MPEGTS_AUDIO.copy(),
                        3: MPEGTS_OTHER.copy()}}),
        ("invalid__empty.ts", {
            "purpose": "Test empty MPEG-TS.",
            "stdout_part": "",
            "stderr_part": "No audio or video tracks found"})
    ])
def test_mediainfo_scraper_mpegts(filename, result_dict, evaluate_scraper):
    """Test MPEG Transport Stream scraping with MediainfoScraper."""
    mimetype = "video/MP2T"
    correct = parse_results(filename, mimetype, result_dict, True)
    scraper = MediainfoScraper(correct.filename, True,
                               params={"mimetype_guess": mimetype})
    scraper.scrape_file()
    for stream in correct.streams.values():
        if stream["mimetype"] == "video/MP2T":
            stream["version"] = "(:unav)"
    if "empty" in filename:
        assert correct.stdout_part in scraper.messages()
        assert correct.stderr_part in scraper.errors()
        assert not scraper.streams
    else:
        evaluate_scraper(scraper, correct)


def test_no_wellformed():
    """Test scraper without well-formed check."""
    scraper = MediainfoScraper("tests/data/audio_x-wav/valid__wav.wav",
                               False, params={"mimetype_guess": "audio/x-wav"})
    scraper.scrape_file()
    assert "Skipping scraper" not in scraper.messages()
    assert scraper.well_formed is None


def test_is_supported_wav():
    """Test is_supported method."""
    mime = "audio/x-wav"
    ver = "2"
    assert MediainfoScraper.is_supported(mime, ver, True)
    assert MediainfoScraper.is_supported(mime, None, True)
    assert MediainfoScraper.is_supported(mime, ver, False)
    assert MediainfoScraper.is_supported(mime, "foo", True)
    assert not MediainfoScraper.is_supported("foo", ver, True)


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
    assert MediainfoScraper.is_supported(mime, ver, True)
    assert MediainfoScraper.is_supported(mime, None, True)
    assert MediainfoScraper.is_supported(mime, ver, False)
    assert MediainfoScraper.is_supported(mime, "foo", True)
    assert not MediainfoScraper.is_supported("foo", ver, True)


def test_no_mime_given():
    """Test that an error is recorded when no MIME type is given."""
    scraper = MediainfoScraper("tests/data/audio_mpeg/valid_1.mp3", True, {})
    with pytest.raises(AttributeError) as error:
        scraper.scrape_file()
    assert (
        "not given a parameter dict containing key 'mimetype_guess'"
        in six.text_type(error.value)
    )
    assert ("not given a parameter dict containing key 'mimetype_guess'" in
            str(error.value))
    assert not scraper.well_formed
    assert not scraper.streams


def run_filetype_test(filename, result_dict, filetype, evaluate_scraper):
    """
    Runs scraper result evaluation for a scraper with forced MIME type/version

    :filename: Name of the file, not containing the tests/data/mime_type/ part
    :result_dict: Result dict to be given to Correct
    :filetype: A dict containing the forced, expected and real file types under
               the following keys:
                * given_mimetype: the forced MIME type
                * given_version: the forced version
                * expected_mimetype: the expected resulting MIME type
                * expected_version: the expected resulting version
                * correct_mimetype: the real MIME type of the file
    """
    correct = force_correct_filetype(filename, result_dict,
                                     filetype)

    if filetype["given_mimetype"]:
        mimetype_guess = filetype["given_mimetype"]
    else:
        mimetype_guess = filetype["correct_mimetype"]
    params = {"mimetype": filetype["given_mimetype"],
              "version": filetype["given_version"],
              "mimetype_guess": mimetype_guess}
    scraper = MediainfoScraper(correct.filename, True, params)
    scraper.scrape_file()

    evaluate_scraper(scraper, correct)


@pytest.mark.parametrize(
    ["filename", "mimetype", "version", "version_result", "streams"],
    [
        ("valid__dv_wav.mov", "video/quicktime", "(:unav)", "(:unav)",
         {0: MOV_CONTAINER.copy(), 1: MOV_DV_VIDEO.copy(), 2: WAV_AUDIO.copy(),
          3: MOV_TC.copy()}),
        ("valid_4_ffv1.mkv", "video/x-matroska", "4", "4",
         {0: MKV_CONTAINER.copy(), 1: FFV_VIDEO.copy()}),
        ("valid_2_bwf.wav", "audio/x-wav", "2", "2",
         {0: WAV_AUDIO.copy()}),
        ("valid_1.mp3", "audio/mpeg", "1", "1",
         {0: MPEG1_AUDIO.copy()}),
    ]
)
def test_forced_filetype(filename, mimetype, version, version_result, streams,
                         evaluate_scraper):
    """
    Tests the simple cases of file type forcing.

    Here, the following cases are tested for one file type scraped using each
    metadata model class supported by MediainfoScraper:
        - Force the scraper to use the correct MIME type and version, which
          should always result in the given MIME type and version and the file
          should be well-formed.
        - Force the scraper to use the correct MIME type, which should always
          result in the given MIME type and the version the metadata model
          would normally return.
        - Give forced version without MIME type, which should result in the
          scraper running normally and not affect its results or messages.
        - Force the scraper to use an unsupported MIME type, which should
          result in an error message being logged and the scraper reporting
          the file as not well-formed.
    """
    # pylint: disable=too-many-arguments
    result_dict = {"purpose": "Test forcing correct MIME type and version",
                   "stdout_part": "MIME type and version not scraped, using",
                   "stderr_part": "",
                   "streams": streams}
    filetype_dict = {"given_mimetype": mimetype,
                     "given_version": version,
                     "expected_mimetype": mimetype,
                     "expected_version": version,
                     "correct_mimetype": mimetype}
    run_filetype_test(filename, result_dict, filetype_dict, evaluate_scraper)
    result_dict = {"purpose": "Test forcing correct MIME type without version",
                   "stdout_part": "MIME type not scraped, using",
                   "stderr_part": "",
                   "streams": streams}
    filetype_dict = {"given_mimetype": mimetype,
                     "given_version": None,
                     "expected_mimetype": mimetype,
                     "expected_version": version_result,
                     "correct_mimetype": mimetype}
    run_filetype_test(filename, result_dict, filetype_dict, evaluate_scraper)

    result_dict = {"purpose": "Test forcing version only (no effect)",
                   "stdout_part": "The file was analyzed successfully",
                   "stderr_part": "",
                   "streams": streams}
    filetype_dict = {"given_mimetype": None,
                     "given_version": "99.9",
                     "expected_mimetype": mimetype,
                     "expected_version": version_result,
                     "correct_mimetype": mimetype}
    run_filetype_test(filename, result_dict, filetype_dict, evaluate_scraper)

    result_dict = {"purpose": "Test forcing wrong MIME type",
                   "stdout_part": "MIME type not scraped, using",
                   "stderr_part": "MIME type not supported",
                   "streams": streams}
    filetype_dict = {"given_mimetype": "unsupported/mime",
                     "given_version": None,
                     "expected_mimetype": "unsupported/mime",
                     "expected_version": version_result,
                     "correct_mimetype": mimetype}
    run_filetype_test(filename, result_dict, filetype_dict, evaluate_scraper)
