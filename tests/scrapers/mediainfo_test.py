"""Test module for Mediainfo.
NOTE: Mediainfo accepts practically any file. We use another scrapers for
well-formed checks.
"""
import pytest
from file_scraper.scrapers.mediainfo import MpegMediainfo, WavMediainfo
from tests.common import parse_results
from tests.scrapers.stream_dicts import MPEG1_VIDEO, MPEG2_VIDEO, \
    MPEG4_CONTAINER, MPEG4_VIDEO, MPEG4_AUDIO, MPEG1_AUDIO, MPEGTS_CONTAINER, \
    MPEGTS_VIDEO, MPEGTS_AUDIO, MPEGTS_OTHER, WAV_AUDIO


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
def test_mediainfo_scraper_wav(filename, result_dict):
    """Test cases for WAV files with Mediainfo"""
    mimetype = 'audio/x-wav'
    correct = parse_results(filename, mimetype, result_dict, True)
    scraper = WavMediainfo(correct.filename, mimetype, True)
    scraper.scrape_file()
    if 'empty' in filename:
        correct.version = None
        correct.streams[0]['version'] = None
        correct.streams[0]['stream_type'] = None

    assert scraper.mimetype == correct.mimetype
    assert scraper.version == correct.version
    assert scraper.streams == correct.streams
    assert scraper.info['class'] == 'WavMediainfo'
    assert correct.stdout_part in scraper.messages()
    assert correct.stderr_part in scraper.errors()
    assert scraper.well_formed == correct.well_formed


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
def test_mediainfo_scraper_mpeg(filename, result_dict):
    """Test cases for MPEG files for MpegMediainfo"""
    mimetype = 'video/mpeg'
    correct = parse_results(filename, mimetype, result_dict, True)
    scraper = MpegMediainfo(correct.filename, mimetype, True)
    scraper.scrape_file()
    if 'empty' in filename:
        correct.version = None
        correct.streams[0]['version'] = None
        correct.streams[0]['stream_type'] = None

    assert scraper.mimetype == correct.mimetype
    assert scraper.version == correct.version
    assert scraper.streams == correct.streams
    assert scraper.info['class'] == 'MpegMediainfo'
    assert correct.stdout_part in scraper.messages()
    assert correct.stderr_part in scraper.errors()
    assert scraper.well_formed == correct.well_formed


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
def test_mediainfo_scraper_mp4(filename, result_dict):
    """Test cases for MP4 files for MpegMediainfo"""
    mimetype = 'video/mp4'
    correct = parse_results(filename, mimetype, result_dict, True)
    scraper = MpegMediainfo(correct.filename, mimetype, True)
    scraper.scrape_file()
    if 'empty' in filename:
        correct.version = None
        correct.streams[0]['version'] = None
        correct.streams[0]['stream_type'] = None

    assert scraper.mimetype == correct.mimetype
    assert scraper.version == correct.version
    assert scraper.streams == correct.streams
    assert scraper.info['class'] == 'MpegMediainfo'
    assert correct.stdout_part in scraper.messages()
    assert correct.stderr_part in scraper.errors()
    assert scraper.well_formed == correct.well_formed


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
def test_mediainfo_scraper_mp3(filename, result_dict):
    """Test cases for MP3 files for MpegMediainfo"""
    mimetype = 'audio/mpeg'
    correct = parse_results(filename, mimetype, result_dict, True)
    scraper = MpegMediainfo(correct.filename, mimetype, True)
    scraper.scrape_file()
    if 'empty' in filename:
        correct.version = None
        correct.streams[0]['version'] = None
        correct.streams[0]['stream_type'] = None

    assert scraper.mimetype == correct.mimetype
    assert scraper.version == correct.version
    assert scraper.streams == correct.streams
    assert scraper.info['class'] == 'MpegMediainfo'
    assert correct.stdout_part in scraper.messages()
    assert correct.stderr_part in scraper.errors()
    assert scraper.well_formed == correct.well_formed


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
def test_mediainfo_scraper_mpegts(filename, result_dict):
    """Test cases for MPEG Transport Stream with MpegMediainfo"""
    mimetype = 'video/MP2T'
    correct = parse_results(filename, mimetype, result_dict, True)
    scraper = MpegMediainfo(correct.filename, mimetype, True)
    scraper.scrape_file()
    if 'empty' in filename:
        correct.version = None
        correct.streams[0]['version'] = None
        correct.streams[0]['stream_type'] = None

    assert scraper.mimetype == correct.mimetype
    assert scraper.version == correct.version
    assert scraper.streams == correct.streams
    assert scraper.info['class'] == 'MpegMediainfo'
    assert correct.stdout_part in scraper.messages()
    assert correct.stderr_part in scraper.errors()
    assert scraper.well_formed == correct.well_formed


@pytest.mark.parametrize(
    ['mime', 'ver'],
    [
        ('video/mpeg', '1'),
        ('video/mp4', ''),
        ('video/MP1S', ''),
        ('video/MP2P', ''),
        ('video/MP2T', ''),
    ]
)
def test_is_supportedi_mpeg(mime, ver):
    """Test is_supported method"""
    assert MpegMediainfo.is_supported(mime, ver, True)
    assert MpegMediainfo.is_supported(mime, None, True)
    assert MpegMediainfo.is_supported(mime, ver, False)
    assert MpegMediainfo.is_supported(mime, 'foo', True)
    assert not MpegMediainfo.is_supported('foo', ver, True)
