"""
Tests for Fido and Magic detectors.

This module tests that:
    - FidoDetector and MagicDetector detect MIME types correctly.
    - FidoDetector returns an empty dict from get_important() with
      certain mimetypes and MagicDetector returns certain mimetypes.
"""
import pytest
from file_scraper.detectors import FidoDetector, MagicDetector
from tests.common import get_files

CHANGE_FIDO = {
    'tests/data/text_plain/valid__ascii.txt': None,
    'tests/data/text_plain/valid__iso8859.txt': None,
    'tests/data/text_plain/valid__utf8.txt': None,
    'tests/data/video_mp4/valid__h264_aac.mp4': None,
    'tests/data/application_msword/valid_11.0.doc': None,
    'tests/data/application_vnd.openxmlformats-officedocument.spreadsheetml'
    '.sheet/valid_15.0.xlsx': None,
    'tests/data/application_vnd.openxmlformats-officedocument.presentationml'
    '.presentation/valid_15.0.pptx': None,
    'tests/data/application_vnd.oasis.opendocument.formula/valid_1.0.odf':
        'application/zip',
    'tests/data/application_x-internet-archive/valid_1.0_.arc.gz':
        'application/gzip',
    'tests/data/application_warc/valid_1.0_.warc.gz': 'application/gzip',
    'tests/data/application_x-internet-archive/valid_1.0.arc': 'text/html',
    'tests/data/video_x-matroska/valid__ffv1.mkv': None}

CHANGE_MAGIC = {
    'tests/data/video_MP2T/valid_.ts': 'application/octet-stream',
    'tests/data/application_x-internet-archive/valid_1.0_.arc.gz':
        'application/x-gzip',
    'tests/data/application_xhtml+xml/valid_1.0.xhtml': 'text/xml',
    'tests/data/application_warc/valid_1.0_.warc.gz': 'application/x-gzip'}


@pytest.mark.parametrize(
    ['detector_class', 'change_dict'],
    [
        (FidoDetector, CHANGE_FIDO),
        (MagicDetector, CHANGE_MAGIC)
    ]
)
def test_detectors(detector_class, change_dict):
    """Test Fido and Magic detectors
    """
    file_dict = get_files(well_formed=True)
    for filename, value in file_dict.iteritems():
        mimetype = value[0]
        detector = detector_class(filename)
        detector.detect()
        if filename in change_dict:
            assert detector.mimetype == change_dict[filename]
        else:
            assert detector.mimetype == mimetype


@pytest.mark.parametrize(
    ['detector_class', 'mimetype'],
    [
        (FidoDetector, 'text/html'),
        (FidoDetector, 'application/zip'),
        (MagicDetector, 'application/vnd.oasis.opendocument.formula'),
        (MagicDetector, 'application/x-internet-archive')
    ]
)
def test_important(detector_class, mimetype):
    """Test important with cruical mimetypes
    """
    detector = detector_class('testfilename')
    detector.mimetype = mimetype
    if detector_class == FidoDetector:
        assert detector.get_important() == {}
    else:
        assert detector.get_important() == {'mimetype': mimetype}
