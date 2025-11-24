"""
Test module for dummy.py

This module tests the following extractor classes:
    - ExtractorNotFound
        - well_formed is None.
        - MIME type and version are what is given to the extractor.
        - Streams contain only one dict with stream_type as None
          and MIME type and version as what was given to the extractor.
    - DetectedMimeVersionExtractor, DetectedMimeVersionMetadataExtractor
        - Results given file format version as a extractor result
        - Results error in MIME type is not supported
"""
from pathlib import Path

import pytest

from file_scraper.defaults import UNAV
from file_scraper.dummy.dummy_extractor import (
    ExtractorNotFound, DetectedMimeVersionExtractor,
    DetectedMimeVersionMetadataExtractor)

DEFAULTSTREAMS = {0: {"index": 0, "version": UNAV,
                      "stream_type": UNAV, "mimetype": UNAV}}


@pytest.mark.parametrize(
    "filepath",
    [
        "tests/data/image_gif/valid_1987a.gif",
        "tests/data/image_gif/valid_1987a.gif",
        "tests/data/image_gif/invalid_1987a_truncated.gif",
        "tests/data/video_x-matroska/valid__ffv1.mkv"
    ]
)
def test_extractor_not_found(filepath):
    """
    Check ExtractorNotFound results.

    :filepath: Test file
    """
    extractor = ExtractorNotFound(Path(filepath), None)
    extractor.extract()

    streams = DEFAULTSTREAMS.copy()

    assert extractor.well_formed is False
    for stream_index, stream_metadata in streams.items():
        extracted_metadata = extractor.streams[stream_index]
        for key, value in stream_metadata.items():
            assert getattr(extracted_metadata, key)() == value


def test_extractor_not_found_with_given_mimetype_and_version():
    """
    Test that ExtractorNotFound retains the MIME type that is given to it
    when scraping the file.
    """
    filename = Path("tests/data/text_plain/valid__ascii.txt")
    expected_mimetype = "expected_mimetype"
    expected_version = "expected_version"
    extractor = ExtractorNotFound(
        filename, mimetype=expected_mimetype, version=expected_version)
    extractor.extract()
    stream = extractor.streams[0]

    assert stream.mimetype() == expected_mimetype
    assert stream.version() == expected_version


def test_detected_version_extractor():
    """Test detected version extractor"""
    filename = Path("tests/data/text_plain/valid__ascii.txt")
    extractor = DetectedMimeVersionMetadataExtractor(
        filename, "text/xml", params={"detected_version": "123"})
    extractor.extract()
    assert extractor.well_formed is False
    assert extractor.streams[0].version() == "123"

    extractor = DetectedMimeVersionMetadataExtractor(
        filename, "text/xml", params=None)
    extractor.extract()
    assert extractor.well_formed is None
    assert extractor.streams[0].version() == "1.0"

    # This test apparently tests that the extractor output validates as False
    extractor = DetectedMimeVersionMetadataExtractor(
        filename, "text/plain", params=None)
    extractor.extract()
    assert len(extractor.errors()) > 0
    assert extractor.streams == []

    extractor = DetectedMimeVersionExtractor(
        filename, "application/x-siard", params={"detected_version": "2.1.1"})
    extractor.extract()
    assert extractor.well_formed is None
    assert extractor.streams[0].version() == "2.1.1"
    assert extractor.streams[0].stream_type() == "binary"

    extractor = DetectedMimeVersionExtractor(
        filename, "application/vnd.oasis.opendocument.text",
        params={"detected_version": "123"})
    extractor.extract()
    assert extractor.well_formed is False
    assert extractor.streams[0].version() == "123"

    extractor = DetectedMimeVersionExtractor(
        filename, "application/epub+zip",
        params={"detected_version": "3"})
    extractor.extract()
    assert extractor.well_formed is None
    assert extractor.streams[0].version() == "3"

    # File format for bit-level preservation
    extractor = DetectedMimeVersionExtractor(
        filename, "application/x.fi-dpres.segy",
        params={"detected_version": "(:unkn)"})
    extractor.extract()
    assert extractor.well_formed is None
    assert extractor.streams[0].mimetype() == "application/x.fi-dpres.segy"
    assert extractor.streams[0].version() == "(:unkn)"
    assert extractor.streams[0].stream_type() == "binary"
