"""Test module for ffmpeg.py"""
import os
import pytest
from file_scraper.scrapers.ffmpeg import FFMpeg
from tests.common import parse_results


@pytest.mark.parametrize(
    ["filename", "result_dict"],
    [
        ("valid_1.m1v", {
            "purpose": "Test valid MPEG-1.",
            "stdout_part": "file was scraped successfully",
            "stderr_part": ""}),
        ("valid_2.m2v", {
            "purpose": "Test valid MPEG-2.",
            "stdout_part": "file was scraped successfully",
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
def test_ffmpeg_scraper_mpeg(filename, result_dict):
    """Test cases for FFMpeg"""
    mimetype = 'video/mpeg'
    correct = parse_results(filename, mimetype, result_dict, True)
    scraper = FFMpeg(correct.filename, mimetype, True)
    scraper.scrape_file()
    correct.version = None
    correct.streams[0]['version'] = None
    correct.streams[0]['stream_type'] = None

    assert scraper.mimetype == correct.mimetype
    assert scraper.version == correct.version
    assert scraper.streams == correct.streams
    assert scraper.info['class'] == 'FFMpeg'
    assert correct.stdout_part in scraper.messages()
    assert correct.stderr_part in scraper.errors()
    assert scraper.well_formed == correct.well_formed


@pytest.mark.parametrize(
    ["filename", "result_dict"],
    [   
        ("valid__h264_aac.mp4", {
            "purpose": "Test valid mp4.",
            "stdout_part": "file was scraped successfully",
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
def test_ffmpeg_scraper_mp4(filename, result_dict):
    """Test cases for FFMpeg"""
    mimetype = 'video/mp4'
    correct = parse_results(filename, mimetype, result_dict, True)
    scraper = FFMpeg(correct.filename, mimetype, True)
    scraper.scrape_file()
    correct.version = None
    correct.streams[0]['version'] = None
    correct.streams[0]['stream_type'] = None

    assert scraper.mimetype == correct.mimetype
    assert scraper.version == correct.version
    assert scraper.streams == correct.streams
    assert scraper.info['class'] == 'FFMpeg'
    assert correct.stdout_part in scraper.messages()
    assert correct.stderr_part in scraper.errors()
    assert scraper.well_formed == correct.well_formed


@pytest.mark.parametrize(
    ["filename", "result_dict"],
    [   
        ("valid_1.mp3", {
            "purpose": "Test valid mp3.",
            "stdout_part": "file was scraped successfully",
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
def test_ffmpeg_scraper_mp3(filename, result_dict):
    """Test cases for FFMpeg"""
    mimetype = 'audio/mpeg'
    correct = parse_results(filename, mimetype, result_dict, True)
    scraper = FFMpeg(correct.filename, mimetype, True)
    scraper.scrape_file()
    correct.version = None
    correct.streams[0]['version'] = None
    correct.streams[0]['stream_type'] = None

    assert scraper.mimetype == correct.mimetype
    assert scraper.version == correct.version
    assert scraper.streams == correct.streams
    assert scraper.info['class'] == 'FFMpeg'
    assert correct.stdout_part in scraper.messages()
    assert correct.stderr_part in scraper.errors()
    assert scraper.well_formed == correct.well_formed


@pytest.mark.parametrize(
    ["filename", "result_dict"],
    [   
        ("valid_.ts", {
            "purpose": "Test valid MPEG-TS.",
            "stdout_part": "file was scraped successfully",
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
def test_ffmpeg_scraper_mpegts(filename, result_dict):
    """Test cases for FFMpeg"""
    mimetype = 'video/MP2T'
    correct = parse_results(filename, mimetype, result_dict, True)
    scraper = FFMpeg(correct.filename, mimetype, True)
    scraper.scrape_file()
    correct.version = None
    correct.streams[0]['version'] = None
    correct.streams[0]['stream_type'] = None

    assert scraper.mimetype == correct.mimetype
    assert scraper.version == correct.version
    assert scraper.streams == correct.streams
    assert scraper.info['class'] == 'FFMpeg'
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
    assert FFMpeg.is_supported(mime, ver, True)
    assert FFMpeg.is_supported(mime, None, True)
    assert not FFMpeg.is_supported(mime, ver, False)
    assert FFMpeg.is_supported(mime, 'foo', True)
    assert not FFMpeg.is_supported('foo', ver, True)
