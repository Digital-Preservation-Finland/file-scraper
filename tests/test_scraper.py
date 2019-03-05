"""Tests
"""
from dpres_scraper.scraper import Scraper


AUDIO = {'audio_data_encoding': 'AAC',
         'bits_per_sample': '0',
         'codec_creator_app': 'Lavf53.24.2',
         'codec_creator_app_version': '53.24.2',
         'codec_name': 'AAC',
         'codec_quality': 'lossy',
         'data_rate': '384',
         'data_rate_mode': 'Variable',
         'duration': 'PT5.31S',
         'index': 2,
         'mimetype': 'audio/mp4',
         'num_channels': '6',
         'sampling_frequency': '48',
         'stream_type': 'audio',
         'version': ''}

VIDEO = {'bits_per_sample': '8',
         'codec_creator_app': 'Lavf53.24.2',
         'codec_creator_app_version': '53.24.2',
         'codec_name': 'AVC',
         'codec_quality': 'lossy',
         'color': 'Color',
         'dar': '1.778',
         'data_rate': '1.205959',
         'data_rate_mode': 'Variable',
         'duration': 'PT5.28S',
         'frame_rate': '25',
         'height': '720',
         'index': 1,
         'mimetype': 'video/mp4',
         'par': '1',
         'sampling': '4:2:0',
         'signal_format': '(:unap)',
         'sound': 'Yes',
         'stream_type': 'video',
         'version': '',
         'width': '1280'}


def test_scraper_mp4():
    """Test mpeg-4 container with video and audio
    """
    scraper = Scraper('./tests/data/video/mp4.mp4')
    scraper.scrape()
    assert cmp(AUDIO, scraper.streams[2]) == 0
    assert cmp(VIDEO, scraper.streams[1]) == 0
    assert scraper.mimetype == 'video/mp4'
    assert scraper.version == ''


def test_scraper_mpg():
    """Test mpeg-1 video
    """
    scraper = Scraper('./tests/data/video/mpg1.mpg')
    scraper.scrape()
    assert scraper.streams is not None
    assert scraper.mimetype == 'video/mpeg'
    assert scraper.version == '1'


def test_scraper_tiff():
    """Test tiff image
    """
    scraper = Scraper('./tests/data/images/tiff1.tif')
    scraper.scrape()
    assert scraper.streams is not None
    assert scraper.mimetype == 'image/tiff'
    assert scraper.version == '6.0'


def test_scraper_txt():
    """Test text file
    """
    scraper = Scraper('./tests/data/text/text.txt')
    scraper.scrape()
    assert scraper.mimetype == 'text/plain'
    assert scraper.version == ''
    assert scraper.streams is not None


def test_scraper_xml():
    """Test xml file
    """
    scraper = Scraper('./tests/data/text/xml.xml')
    scraper.scrape()
    assert scraper.mimetype == 'text/xml'
    assert scraper.version == '1.0'
    assert scraper.streams is not None
