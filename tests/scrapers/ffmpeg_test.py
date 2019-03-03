"""
This is a test for ffmpeg.py.
"""
import os

from ipt.validator.ffmpeg import FFMpeg

TEST_DATA_PATH = 'tests/data/02_filevalidation_data/mpg'


def check_ffmpeg_ok(filename, mimetype, version, video=None, audio=None,
                    video_streams=None, audio_streams=None):
    """
    Checker function.
    """

    file_path = os.path.join(TEST_DATA_PATH, filename)

    metadata_info = {
        "filename": file_path,
        "format": {
            "version": version,
            "mimetype": mimetype}
        }
    if video:
        metadata_info["video"] = video
    if audio:
        metadata_info["audio"] = audio
    if video_streams:
        metadata_info["video_streams"] = video_streams
    if audio_streams:
        metadata_info["audio_streams"] = audio_streams

    validator = FFMpeg(metadata_info=metadata_info)
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
        video={
            'bit_rate': '0.32',
            'width': '320',
            'height': '240',
            'display_aspect_ratio': '1.33',
            'avg_frame_rate': '29.97'})

    check_ffmpeg_ok(
        filename="mpg2.mpg",
        mimetype="video/MP2P",
        version=None,
        video_streams=[
            {"format": {"mimetype": "video/mpeg",
                        "version": "2"},
             "video": {"width": '320',
                       "height": '240',
                       "display_aspect_ratio": '1.33',
                       "avg_frame_rate": "29.97"}}])

    check_ffmpeg_ok(
        filename="mp4.mp4",
        mimetype="video/mp4",
        version=None,
        video_streams=[
            {"format": {"mimetype": "video/mp4",
                        "version": None},
             "video": {"width": '1280',
                       "height": '720',
                       "display_aspect_ratio": "1.78",
                       "avg_frame_rate": "25"}}],
        audio_streams=[
            {"format": {"mimetype": "audio/mp4",
                        "version": None},
             "audio": {"sample_rate": "48",
                       "bit_rate": "384",
                       "channels": "6"}}])

    check_ffmpeg_ok(
        filename="valid_mp3.mp3",
        mimetype="audio/mpeg",
        version="1",
        audio={"sample_rate": "48",
               "bit_rate": "64",
               "channels": "1"})


def check_ffmpeg_nok(filename, mimetype, version, video=None, audio=None,
                     video_streams=None, audio_streams=None):
    """
    Checker function.
    """

    file_path = os.path.join(TEST_DATA_PATH, filename)

    metadata_info = {
        "filename": file_path,
        "format": {
            "version": version,
            "mimetype": mimetype}
        }
    if video:
        metadata_info["video"] = video
    if audio:
        metadata_info["audio"] = audio
    if video_streams:
        metadata_info["video_streams"] = video_streams
    if audio_streams:
        metadata_info["audio_streams"] = audio_streams

    validator = FFMpeg(metadata_info=metadata_info)
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
        video={
            'bit_rate': '0.32',
            'width': 320,
            'height': 240,
            'display_aspect_ratio': '1.33',
            'avg_frame_rate': '29.97'})

    check_ffmpeg_nok(
        filename="mpg1_error2.mpg",
        mimetype="video/mpeg",
        version="1",
        video={
            'bit_rate': '0.32',
            'width': 320,
            'height': 240,
            'display_aspect_ratio': '1.33',
            'avg_frame_rate': '29.97'})

    check_ffmpeg_nok(
        filename="mp4_error.mp4",
        mimetype="video/mp4",
        version=None,
        video_streams=[
            {"format": {"mimetype": "video/mp4",
                        "version": None},
             "video": {"width": '1280',
                       "height": '720',
                       "display_aspect_ratio": "1.78",
                       "avg_frame_rate": "25"}}],
        audio_streams=[
            {"format": {"mimetype": "audio/mp4",
                        "version": None},
             "audio": {"sample_rate": "48",
                       "bit_rate": "384",
                       "channels": "6"}}])

    check_ffmpeg_nok(
        filename="mpg2_error.mpg",
        mimetype="video/mpeg",
        version="2",
        video={
            "width": '320',
            "height": '240',
            'display_aspect_ratio': '1.33',
            "avg_frame_rate": "29.97"})

    check_ffmpeg_nok(
        filename="mpg1.mpg",
        mimetype="video/mpeg",
        version="4",
        video={
            'width': '320',
            'height': '240',
            'display_aspect_ratio': '1.33',
            'avg_frame_rate': '29.97'})

    check_ffmpeg_nok(
        filename="unknown_mimetype.3gp",
        mimetype="video/mpeg",
        version="2",
        video_streams=[
            {"format": {"mimetype": "video/mpeg",
                        "version": "2"},
             "video": {"width": '176',
                       "height": '144',
                       "avg_frame_rate": "15"}}],
        audio_streams=[
            {"format": {"mimetype": "audio/mpeg",
                        "version": "2"},
             "audio": {"sample_rate": "8",
                       "channels": "1"}}])

    check_ffmpeg_nok(
        filename="no_video.wav",
        mimetype="video/mpeg",
        version="1",
        audio={"channels": "2"})

    check_ffmpeg_nok(
        filename="mpg1.mpg",
        mimetype="video/mpeg",
        version="1",
        video_streams=[
            {"format": {"mimetype": "video/mpeg",
                        "version": "1"},
             "video": {"width": '320',
                       "height": '240',
                       "bit_rate": '0.32',
                       'display_aspect_ratio': '1.33',
                       "avg_frame_rate": "29.97"}},
            {"format": {"mimetype": "video/mpeg",
                        "version": "1"},
             "video": {"width": '320',
                       "height": '240',
                       "bit_rate": '0.32',
                       'display_aspect_ratio': '1.33',
                       "avg_frame_rate": "29.97"}}])

    check_ffmpeg_nok(
        filename="mpg1.mpg",
        mimetype="video/mpeg",
        version="1")
