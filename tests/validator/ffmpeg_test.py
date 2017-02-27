"""
This is a test for ffmpeg.py.
"""
import os

from ipt.validator.ffmpeg import FFMpeg

TEST_DATA_PATH = 'tests/data/02_filevalidation_data/mpg'


def check_ffmpeg_ok(filename, mimetype, version, videomd=None, audiomd=None):
    """
    Checker function.
    """

    file_path = os.path.join(TEST_DATA_PATH, filename)

    fileinfo = {
        "filename": file_path,
        "format": {
            "version": version,
            "mimetype": mimetype}
        }
    if videomd:
        fileinfo["video"] = videomd
    if audiomd:
        fileinfo["audio"] = audiomd

    validator = FFMpeg(fileinfo=fileinfo)
    validator.validate()

    assert validator.messages() != ""
    assert validator.is_valid, validator.errors()
    assert validator.errors() == ""


def test_mark_ffmpeg_ok():
    """FFMpeg test."""

    check_ffmpeg_ok(
        filename="mpg1.mpg",
        mimetype="video/mpeg",
        version="1",
        videomd=[
            {'codec_name': 'MPEG 1',
             'sample_aspect_ratio': '1:1',
             'level': '-99',
             'duration': '19.025400',
             'width': '320',
             'display_aspect_ratio': '4:3',
             'height': '240',
             'avg_frame_rate': '30000/1001'}])

    check_ffmpeg_ok(
        filename="mpg2.mpg",
        mimetype="video/MP2P",
        version="2",
        videomd=[
            {"codec_name": "MPEG 2",
             "width": '320',
             "height": '240',
             "sample_aspect_ratio": "1:1",
             "display_aspect_ratio": "4:3",
             "level": '8',
             "avg_frame_rate": "30000/1001",
             "duration": "19.019000"}])

    check_ffmpeg_ok(
        filename="mp4.mp4",
        mimetype="video/mp4",
        version="",
        videomd=[
            {"codec_name": "AVC",
             "width": '1280',
             "height": '720',
             "sample_aspect_ratio": "1:1",
             "display_aspect_ratio": "16:9",
             "level": '31',
             "avg_frame_rate": "25/1",
             "duration": "5.280000"}],
        audiomd=[
            {"codec_name": "AAC",
             "sample_rate": "48000",
             "duration": "5.312000",
             "channels": "6"}])


def check_ffmpeg_nok(filename, mimetype, version, videomd=None, audiomd=None):
    """
    Checker function.
    """

    file_path = os.path.join(TEST_DATA_PATH, filename)

    fileinfo = {
        "filename": file_path,
        "format": {
            "version": version,
            "mimetype": mimetype}
        }
    if videomd:
        fileinfo["video"] = videomd
    if audiomd:
        fileinfo["audio"] = audiomd

    validator = FFMpeg(fileinfo=fileinfo)
    validator.validate()

    assert not validator.is_valid
    assert validator.errors() != ""


def test_mark_ffmpeg_nok():
    """
    Test for failed validation
    """

    check_ffmpeg_nok(
        filename="mpg1_error.mpg",
        mimetype="video/mpeg",
        version="1",
        videomd=[
            {'codec_name': 'MPEG 1',
             'sample_aspect_ratio': '1:1',
             'level': -99,
             'duration': '19.025400',
             'width': 320,
             'codec_long_name': 'MPEG-1 video',
             'display_aspect_ratio': '4:3',
             'height': 240,
             'avg_frame_rate': '30000/1001'}])

    check_ffmpeg_nok(
        filename="mpg1_error2.mpg",
        mimetype="video/mpeg",
        version="1",
        videomd=[
            {'codec_name': 'MPEG 1',
             'sample_aspect_ratio': '1:1',
             'level': -99,
             'duration': '19.025400',
             'width': 320,
             'codec_long_name': 'MPEG-1 video',
             'display_aspect_ratio': '4:3',
             'height': 240,
             'avg_frame_rate': '30000/1001'}])

    check_ffmpeg_nok(
        filename="mp4_error.mp4",
        mimetype="video/mp4",
        version="",
        videomd=[
            {"codec_name": "AVC",
             "width": '1280',
             "height": '720',
             "sample_aspect_ratio": "1:1",
             "display_aspect_ratio": "16:9",
             "level": '31',
             "avg_frame_rate": "25/1",
             "duration": "5.280000"}],
        audiomd=[
            {"codec_name": "AAC",
             "sample_rate": "48000",
             "duration": "5.312000",
             "channels": "6"}])

    check_ffmpeg_nok(
        filename="mpg2_error.mpg",
        mimetype="video/mpeg",
        version="2",
        videomd=[
            {"codec_name": "MPEG 2",
             "width": '320',
             "height": '240',
             "sample_aspect_ratio": "1:1",
             "display_aspect_ratio": "4:3",
             "level": '8',
             "avg_frame_rate": "30000/1001",
             "duration": "18.985633"}])

    check_ffmpeg_nok(
        filename="mpg1.mpg",
        mimetype="video/mpeg",
        version="4",
        videomd=[
            {'codec_name': 'MPEG 1',
             'sample_aspect_ratio': '1:1',
             'level': '-99',
             'duration': '19.025400',
             'width': '320',
             'display_aspect_ratio': '4:3',
             'height': '240',
             'avg_frame_rate': '30000/1001'}])

    check_ffmpeg_nok(
        filename="unknown_mimetype.3gp",
        mimetype="video/mpeg",
        version="2",
        videomd=[
            {"codec_name": "AVC",
             "width": 176,
             "height": 144,
             "sample_aspect_ratio": "1:1",
             "display_aspect_ratio": "11:9",
             "avg_frame_rate": "15/1",
             "duration": "4.933333",
             "level": "0"}],
        audiomd=[
            {"codec": "amrnb",
             "sample_rate": "8000",
             "duration": "5.000000",
             "channels": "1"}])

    check_ffmpeg_nok(
        filename="no_video.wav",
        mimetype="video/mpeg",
        version="1",
        audiomd=[
            {"codec_name": "wav",
             "duration": "2.936625",
             "channels": "2"}])

    check_ffmpeg_nok(
        filename="mpg1.mpg",
        mimetype="video/mpeg",
        version="1",
        videomd=[
            {'codec_name': 'MPEG 1',
             'sample_aspect_ratio': '1:1',
             'level': '-99',
             'duration': '19.025400',
             'width': '320',
             'display_aspect_ratio': '4:3',
             'height': '240',
             'avg_frame_rate': '30000/1001'},
            {'codec_name': 'MPEG 1',
             'sample_aspect_ratio': '1:1',
             'level': '-99',
             'duration': '19.025400',
             'width': '320',
             'display_aspect_ratio': '4:3',
             'height': '240',
             'avg_frame_rate': '30000/1001'}])

    check_ffmpeg_nok(
        filename="mpg1.mpg",
        mimetype="video/mpeg",
        version="1")
