"""Module to test the default constants that were set."""

import pytest

from file_scraper.detectors import MagicDetector
from file_scraper.defaults import PRONOM_DICT, VERSION_DICT, MIMETYPE_DICT


@pytest.mark.parametrize(
    ["constant_dict", "expected_type"],
    [
        [PRONOM_DICT, tuple],
        [VERSION_DICT, dict],
    ]
)
def test_constants_syntax(constant_dict, expected_type):
    """A simple test to ensure that the two complicated constants, PRONON_DICT
    and VERSION_DICT, will have appropriate type for their value.
    """
    for value in constant_dict.values():
        assert isinstance(value, expected_type)


def test_mimetype_dict(monkeypatch):
    """
    Test mapped mimetypes by mocking file_scraper.detectors.magic_analyze
    """
    TEST_MIMETYPE_DICT = {
        "application/xml": "text/xml",
        "application/mp4": None,
        "application/vnd.ms-asf": "video/x-ms-asf",
        "application/x-wine-extension-ini": "text/plain",
        "video/x-msvideo": "video/avi",
        "video/x-dv": "video/dv",
        "audio/x-ms-wma": "video/x-ms-asf",
        "video/x-ms-wmv": "video/x-ms-asf",
        "audio/x-m4a": "audio/mp4",
    }
    for key, value in TEST_MIMETYPE_DICT.items():
        def mock_analyze(magic_lib, magic_type, path):
            return key
        monkeypatch.setattr('file_scraper.detectors.magic_analyze',
                            mock_analyze)
        detector = MagicDetector(
            "tests/data/text_plain/valid__utf8_without_bom.txt")
        detector.detect()
        assert detector.mimetype == value
