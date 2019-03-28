"""
Test module for ffmpeg.py

This module tests that:
    - For valid MPEG-1 and MPEG-2 files the scraping is reported as successful,
      the file is well-formed and other properties are:
        - mimetype is video/mpeg
        - version is None
        - in streams, version and stream_type are None
    - For empty MPEG files the results are similar but file is not well-formed
      and errors should contain message 'Invalid data found when processing
      input'.
    - For MPEG files with missing data the file is not well-formed and errors
      should contain "end mismatch".

    - For valid mp4 files with h.264 video and AAC audio the scraping is
      reported as successful, the file is well-formed and other properties are:
        - mimetype is video/mp4
        - version is None
        - in streams, version and stream_type are None
    - For empty mp4 files, the results are similar but file is not well-formed
      and errors should contain message 'Invalid data found when processing
      input'
    - For mp4 files with missing data the file is not well-formed and errors
      should contain "end mismatch"

    - For valid mp3 files the scraping is reported as successful, the file is
      well-formed and its other properties are:
        - mimetype is audio/mpeg
        - version is None
        - in streams, version and stream_type are None
    - For empty mp3 files, the results are similar but file is not well-formed
      and errors should contain message 'could not find codec parameters'.
    - For mp3 files with missing data, the file is not well-formed and errors
      should contain 'Error while decoding stream'.
    - For mp3 files with wrong version reported in the header, the file is not
      well-formed and errors should contain 'Error while decoding stream'.

    - For valid MPEG-TS files the scraping is reported as successful, the file
      is well-formed and its other properties are:
        - mimetype is 'video/MP2T'
        - version is None
        - in streams, version and stream_type are None
    - For empty MPEG-TS files, the results are ismilar but file is not well-
      formed and errors should contain message 'Invalid data found when
      processing input'.
    - For MPEG-TS files with missing data, the file is not well-formed and
      errors should contain "invalid new backstep".

    - When the scraper is run without well-formed check on a well-formed file,
      well_formed is None and scraper messages contain 'Skipping scraper'.

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
from file_scraper.scrapers.ffmpeg import FFMpegWellformed
from tests.common import parse_results


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
def test_ffmpeg_scraper_mpeg(filename, result_dict):
    """Test FFMpegWellformed."""
    mimetype = 'video/mpeg'
    correct = parse_results(filename, mimetype, result_dict, True)
    scraper = FFMpegWellformed(correct.filename, mimetype, True)
    scraper.scrape_file()
    correct.version = None
    correct.streams[0]['version'] = None
    correct.streams[0]['stream_type'] = None

    assert scraper.mimetype == correct.mimetype
    assert scraper.version == correct.version
    assert scraper.streams == correct.streams
    assert scraper.info['class'] == 'FFMpegWellformed'
    assert correct.stdout_part in scraper.messages()
    assert correct.stderr_part in scraper.errors()
    assert scraper.well_formed == correct.well_formed


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
def test_ffmpeg_scraper_mp4(filename, result_dict):
    """Test FFMpegWellformed."""
    mimetype = 'video/mp4'
    correct = parse_results(filename, mimetype, result_dict, True)
    scraper = FFMpegWellformed(correct.filename, mimetype, True)
    scraper.scrape_file()
    correct.version = None
    correct.streams[0]['version'] = None
    correct.streams[0]['stream_type'] = None


    assert scraper.mimetype == correct.mimetype
    assert scraper.version == correct.version
    assert scraper.streams == correct.streams
    assert scraper.info['class'] == 'FFMpegWellformed'
    assert correct.stdout_part in scraper.messages()
    assert correct.stderr_part in scraper.errors()
    assert scraper.well_formed == correct.well_formed


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
def test_ffmpeg_scraper_mp3(filename, result_dict):
    """Test FFMpegWellformed."""
    mimetype = 'audio/mpeg'
    correct = parse_results(filename, mimetype, result_dict, True)
    scraper = FFMpegWellformed(correct.filename, mimetype, True)
    scraper.scrape_file()
    correct.version = None
    correct.streams[0]['version'] = None
    correct.streams[0]['stream_type'] = None

    assert scraper.mimetype == correct.mimetype
    assert scraper.version == correct.version
    assert scraper.streams == correct.streams
    assert scraper.info['class'] == 'FFMpegWellformed'
    assert correct.stdout_part in scraper.messages()
    assert correct.stderr_part in scraper.errors()
    assert scraper.well_formed == correct.well_formed


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
def test_ffmpeg_scraper_mpegts(filename, result_dict):
    """Test FFMpegWellformed."""
    mimetype = 'video/MP2T'
    correct = parse_results(filename, mimetype, result_dict, True)
    scraper = FFMpegWellformed(correct.filename, mimetype, True)
    scraper.scrape_file()
    correct.version = None
    correct.streams[0]['version'] = None
    correct.streams[0]['stream_type'] = None

    assert scraper.mimetype == correct.mimetype
    assert scraper.version == correct.version
    assert scraper.streams == correct.streams
    assert scraper.info['class'] == 'FFMpegWellformed'
    assert correct.stdout_part in scraper.messages()
    assert correct.stderr_part in scraper.errors()
    assert scraper.well_formed == correct.well_formed


def test_no_wellformed():
    """Test scraper without well-formed check."""
    scraper = FFMpegWellformed('tests/data/video_mpeg/valid_1.m1v',
                               'video/mpeg', False)
    scraper.scrape_file()
    assert 'Skipping scraper' in scraper.messages()
    assert scraper.well_formed is None


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
def test_is_supported_mpeg(mime, ver):
    """Test is_supported method."""
    assert FFMpegWellformed.is_supported(mime, ver, True)
    assert FFMpegWellformed.is_supported(mime, None, True)
    assert not FFMpegWellformed.is_supported(mime, ver, False)
    assert FFMpegWellformed.is_supported(mime, 'foo', True)
    assert not FFMpegWellformed.is_supported('foo', ver, True)
