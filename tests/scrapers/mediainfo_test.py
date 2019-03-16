"""Test module for mediainfo.py"""
import os
import pytest
from file_scraper.scrapers.mediainfo import VideoMediainfo, MpegMediainfo
from tests.scrapers.common import parse_results

TESTDATADIR_BASE = 'tests/data'


@pytest.mark.parametrize(
    ["filename", "result_dict", "mimetype", "scraper_class"],
    [
#        ("addme.mov", { #TODO lisaa VideoMediainfolla scrapettavia tiedostoja
#            "purpose": "Test valid ______.",
#            "stdout_part": "file was scraped successfully",
#            "stderr_part": ""},
#         "mime/type", VideoMediainfo),
        ("valid_1.m1v", {
            "purpose": "Test valid MPEG-1.",
            "stdout_part": "file was scraped successfully",
            "stderr_part": "",
            "streams": {0: {'mimetype': 'video/mpeg', 'index': 0,
                            'stream_type': 'videocontainer', 'version': '1',
                            'codec_name': 'MPEG Video',
                            'codec_creator_app_version': '(:unav)',
                            'codec_creator_app': '(:unav)'},
                        1: {'mimetype': 'video/mpeg', 'index': 1, 'par': '1',
                            'frame_rate': '30', 'data_rate': '0.171304',
                            'bits_per_sample': '8',
                            'data_rate_mode':'Variable', 'color': 'Color',
                            'codec_quality': 'lossy',
                            'signal_format': '(:unap)', 'dar': '1.778',
                            'height': '180', 'sound': 'No', 'version': '1',
                            'codec_name': 'MPEG Video',
                            'codec_creator_app_version': '(:unav)',
                            'duration': 'PT1S', 'sampling': '4:2:0',
                            'stream_type': 'video', 'width': '320',
                            'codec_creator_app': '(:unav)'}}},
         "video/mpeg", MpegMediainfo),
        ("valid_2.m2v", {
            "purpose": "Test valid MPEG-2.",
            "stdout_part": "file was scraped successfully",
            "stderr_part": "",
            "streams": {0: {'mimetype': 'video/mpeg', 'index': 0,
                            'stream_type': 'videocontainer', 'version': '2',
                            'codec_name': 'MPEG Video',
                            'codec_creator_app_version': '(:unav)',
                            'codec_creator_app': '(:unav)'},
                        1: {'mimetype': 'video/mpeg', 'index': 1, 'par': '1',
                            'frame_rate': '30', 'data_rate': '0.185784',
                            'bits_per_sample': '8',
                            'data_rate_mode': 'Variable',
                            'color': 'Color', 'codec_quality': 'lossy',
                            'signal_format': '(:unap)', 'dar': '1.778',
                            'height': '180', 'sound': 'No', 'version': '2',
                            'codec_name': 'MPEG Video',
                            'codec_creator_app_version': '(:unav)',
                            'duration': 'PT1S', 'sampling': '4:2:0',
                            'stream_type': 'video', 'width': '320',
                            'codec_creator_app': '(:unav)'}}},
         "video/mpeg", MpegMediainfo),
        ("valid__h264_aac.mp4", {
            "purpose": "Test valid mp4.",
            "stdout_part": "file was scraped successfully",
            "stderr_part": "",
            "streams": {0: {'mimetype': 'video/mp4', 'index': 0,
                            'stream_type': 'videocontainer', 'version': '',
                            'codec_name': 'MPEG-4',
                            'codec_creator_app_version': '56.40.101',
                            'codec_creator_app': 'Lavf56.40.101'},
                        1: {'mimetype': 'video/mp4', 'index': 1, 'par': '1',
                            'frame_rate': '30', 'data_rate': '0.048704',
                            'bits_per_sample': '8',
                            'data_rate_mode': 'Variable',
                            'color': 'Color', 'codec_quality': 'lossy',
                            'signal_format': '(:unap)',
                            'dar': '1.778', 'height': '180', 'sound': 'Yes',
                            'version': '', 'codec_name': 'AVC',
                            'codec_creator_app_version': '56.40.101',
                            'duration': 'PT1S', 'sampling': '4:2:0',
                            'stream_type': 'video', 'width': '320',
                            'codec_creator_app': 'Lavf56.40.101'},
                        2: {'mimetype': 'audio/mp4', 'index': 2,
                            'audio_data_encoding': 'AAC',
                            'bits_per_sample': '0',
                            'data_rate_mode': 'Fixed',
                            'codec_quality': 'lossy',
                            'version': '', 'stream_type': 'audio',
                            'sampling_frequency': '44.1',
                            'num_channels': '2', 'codec_name': 'AAC',
                            'codec_creator_app_version': '56.40.101',
                            'duration': 'PT0.86S', 'data_rate': '135.233',
                            'codec_creator_app': 'Lavf56.40.101'}}},
         "video/mp4", MpegMediainfo),
        ("valid_1.mp3", {
            "purpose": "Test valid mp3.",
            "stdout_part": "file was scraped successfully",
            "stderr_part": "",
            "streams": {0: {'mimetype': 'audio/mpeg', 'index': 0,
                            'stream_type': 'videocontainer', 'version': '',
                            'codec_name': 'MPEG Audio',
                            'codec_creator_app_version': '(:unav)',
                            'codec_creator_app': '(:unav)'},
                        1: {'mimetype': 'audio/mpeg', 'index': 1,
                            'audio_data_encoding': 'MPEG Audio',
                            'bits_per_sample': '0',
                            'data_rate_mode': 'Variable',
                            'codec_quality': 'lossy', 'version': '1',
                            'stream_type': 'audio',
                            'sampling_frequency': '44.1',
                            'num_channels': '2', 'codec_name': 'MPEG Audio',
                            'codec_creator_app_version': '(:unav)',
                            'duration': '(:unav)', 'data_rate': '0',
                            'codec_creator_app': '(:unav)'}}},
         "audio/mpeg", MpegMediainfo)
    ])
def test_mediainfo_scrapers(filename, result_dict, mimetype, scraper_class):
    """Test cases for VideoMediainfo"""

    correct = parse_results(filename, mimetype, result_dict, True)
    scraper = scraper_class(os.path.join(TESTDATADIR_BASE,
                                         mimetype.replace('/', '_'),
                                         filename),
                            mimetype, True)
    scraper.scrape_file()

    assert scraper.mimetype == correct.mimetype
    assert not scraper.version or scraper.version == correct.version
    assert scraper.streams == correct.streams
    assert scraper.info['class'] == 'MpegMediainfo'
    assert correct.stdout_part in scraper.messages()
    assert correct.stderr_part in scraper.errors()
    assert scraper.well_formed == correct.well_formed
