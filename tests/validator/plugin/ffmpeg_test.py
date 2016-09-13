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
        videomd=[{"codec": "mpeg1video"}])

    check_ffmpeg_ok(
        filename="mpg2.mpg",
        mimetype="video/mpeg",
        version="2",
        videomd=[{"codec": "mpeg2video"}])

    check_ffmpeg_ok(
        filename="mp4.mp4",
        mimetype="video/mp4",
        version="",
        videomd=[{"codec": "h264"}],
        audiomd=[{"codec": "aac"}])


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
        videomd=[{"codec": "mpeg1video"}])

    check_ffmpeg_nok(
        filename="mpg1_error2.mpg",
        mimetype="video/mpeg",
        version="1",
        videomd=[{"codec": "mpeg1video"}])

    check_ffmpeg_nok(
        filename="mp4_error.mp4",
        mimetype="video/mp4",
        version="")

    check_ffmpeg_nok(
        filename="mpg2_error.mpg",
        mimetype="video/mpeg",
        version="2",
        videomd=[{"codec": "mpeg2video"}])

    check_ffmpeg_nok(
        filename="mpg1.mpg",
        mimetype="video/mpeg",
        version="4",
        videomd=[{"codec": "mpeg1video"}])

    check_ffmpeg_nok(
        filename="unknown_mimetype.3gp",
        mimetype="video/mpeg",
        version="2",
        videomd=[{"codec": "mpeg4"}],
        audiomd=[{"codec": "amrnb"}])

    check_ffmpeg_nok(
        filename="no_video.wav",
        mimetype="video/mpeg",
        version="1",
        audiomd=[{"codec": "wav"}])
