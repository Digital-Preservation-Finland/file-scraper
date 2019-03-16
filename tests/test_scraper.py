"""These are initial tests, and will be changed later
"""
from file_scraper.scraper import Scraper

CONTAINER = {'codec_creator_app': 'Lavf56.40.101',
             'codec_creator_app_version': '56.40.101',
             'codec_name': 'MPEG-4',
             'index': 0,
             'mimetype': 'video/mp4',
             'stream_type': 'videocontainer',
             'version': ''}

VIDEO = {'bits_per_sample': '8',
         'codec_creator_app': 'Lavf56.40.101',
         'codec_creator_app_version': '56.40.101',
         'codec_name': 'AVC',
         'codec_quality': 'lossy',
         'color': 'Color',
         'dar': '1.778',
         'data_rate': '0.048704',
         'data_rate_mode': 'Variable',
         'duration': 'PT1S',
         'frame_rate': '30',
         'height': '180',
         'index': 1,
         'mimetype': 'video/mp4',
         'par': '1',
         'sampling': '4:2:0',
         'signal_format': '(:unap)',
         'sound': 'Yes',
         'stream_type': 'video',
         'version': '',
         'width': '320'}

AUDIO = {'audio_data_encoding': 'AAC',
         'bits_per_sample': '0',
         'codec_creator_app': 'Lavf56.40.101',
         'codec_creator_app_version': '56.40.101',
         'codec_name': 'AAC',
         'codec_quality': 'lossy',
         'data_rate': '135.233',
         'data_rate_mode': 'Fixed',
         'duration': 'PT0.86S',
         'index': 2,
         'mimetype': 'audio/mp4',
         'num_channels': '2',
         'sampling_frequency': '44.1',
         'stream_type': 'audio',
         'version': ''}


def test_scraper_mp4():
    """Test mpeg-4 container with video and audio
    """
    scraper = Scraper('./tests/data/video_mp4/valid_h264_aac.mp4')
    scraper.scrape()
    assert cmp(AUDIO, scraper.streams[2]) == 0
    assert cmp(VIDEO, scraper.streams[1]) == 0
    assert cmp(CONTAINER, scraper.streams[0]) == 0
    assert scraper.mimetype == 'video/mp4'
    assert scraper.version == ''


def test_scraper_mpg():
    """Test mpeg-1 video
    """
    scraper = Scraper('./tests/data/video_mpeg/valid_1.m1v')
    scraper.scrape()
    assert scraper.streams is not None
    assert scraper.mimetype == 'video/mpeg'
    assert scraper.version == '1'


def test_scraper_tiff():
    """Test tiff image
    """
    scraper = Scraper('./tests/data/image_tiff/valid_6.0.tif')
    scraper.scrape()
    assert scraper.streams is not None
    assert scraper.mimetype == 'image/tiff'
    assert scraper.version == '6.0'


def test_scraper_txt():
    """Test text file
    """
    scraper = Scraper('./tests/data/text_plain/valid.txt')
    scraper.scrape()
    assert scraper.mimetype == 'text/plain'
    assert scraper.version == ''
    assert scraper.streams is not None


def test_scraper_xml():
    """Test xml file
    """
    scraper = Scraper('./tests/data/text_xml/valid_1.0.xml')
    scraper.scrape()
    assert scraper.mimetype == 'text/xml'
    assert scraper.version == '1.0'
    assert scraper.streams is not None
