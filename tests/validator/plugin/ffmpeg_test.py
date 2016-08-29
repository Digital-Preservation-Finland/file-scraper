"""
This is a test for ffmpeg.py.
"""
import os
import pytest

from ipt.validator.ffmpeg import FFMpeg

TEST_DATA_DIR_BASE = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '../../data'))
TEST_DATA_PATH = os.path.abspath(
    os.path.join(TEST_DATA_DIR_BASE, '02_filevalidation_data', 'mpg'))


@pytest.mark.parametrize(
    ["mimetype", "filename", "version"], [
        ("video/mpeg", "mpg1.mpg", "1"),
        ("video/mp4", "mp4.mp4", ""),
        ("video/mpeg", "mpg2.mpg", "2")])
def test_mark_ffmpeg_ok(mimetype, filename, version):
    """FFMpeg test."""
    file_path = os.path.join(TEST_DATA_PATH, filename)
    fileinfo = {
        "filename": file_path,
        "format": {
            "version": version,
            "mimetype": mimetype}
        }
    validator = FFMpeg(fileinfo=fileinfo)
    validator.validate()

    assert validator.messages() != ""
    assert validator.is_valid
    assert validator.errors() == ""


@pytest.mark.parametrize(
    ["mimetype", "filename", "version"], [
        ("video/mpeg", "mpg1_error.mpg", "1"),
        ("video/mpeg", "mpg1_error2.mpg", "1"),
        ("video/mp4", "mp4_error.mp4", ""),
        ("video/mpeg", "mpg2_error.mpg", "2"),
        ("video/mpeg", "mpg1.mpg", "4"),
        ("video/mpeg", "unknown_mimetype.3gp", "2"),
        ("video/mpeg", "no_video.wav", "1")])
def test_mark_ffmpeg_nok(mimetype, filename, version):
    """FFMpeg test."""
    file_path = os.path.join(TEST_DATA_PATH, filename)
    fileinfo = {
        "filename": file_path,
        "format": {
            "version": version,
            "mimetype": mimetype}
        }
    validator = FFMpeg(fileinfo=fileinfo)
    validator.validate()

    assert not validator.is_valid
    assert validator.errors() != ""
