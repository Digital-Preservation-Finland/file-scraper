"""Tests for graders."""
from collections import namedtuple

import pytest
from file_scraper.defaults import (
    ACCEPTABLE, RECOMMENDED, UNACCEPTABLE, BIT_LEVEL_WITH_RECOMMENDED)
from file_scraper.graders import MIMEGrader, TextGrader, ContainerStreamsGrader

FakeScraper = namedtuple("FakeScraper", ["mimetype", "version", "streams"])


@pytest.mark.parametrize(
    ('scraper', 'expected_grade'),
    [
        (FakeScraper('application/pdf', 'A-1a', {}), RECOMMENDED),
        (FakeScraper('application/pdf', '1.2', {}), ACCEPTABLE),
        (FakeScraper('application/pdf', 'foo', {}), UNACCEPTABLE)
    ]
)
def test_mime_grader(scraper, expected_grade):
    """Test that Grader gives expected grade for file."""
    grader = MIMEGrader(scraper)
    assert grader.grade() == expected_grade


@pytest.mark.parametrize(
    ('scraper', 'expected_grade'),
    [
        (
            FakeScraper('text/csv', '(:unap)', {0: {"charset": 'UTF-8'}}),
            RECOMMENDED
        ),
        (
            FakeScraper('text/csv', 'foo', {0: {'charset': 'UTF-8'}}),
            UNACCEPTABLE
        ),
        (
            FakeScraper('text/csv', '(:unap)', {0: {'charset': 'foo'}}),
            UNACCEPTABLE
        )
    ]
)
def test_text_grader(scraper, expected_grade):
    """Test that TextGrader gives expected grade for file."""
    grader = TextGrader(scraper)
    assert grader.grade() == expected_grade


@pytest.mark.parametrize(
    ('scraper', 'expected_grade'),
    [
        # All streams recommended
        (
            FakeScraper(
                'video/MP2T', '(:unap)',
                {
                    0: {'mimetype': 'video/MP2T', 'version': '(:unap)'},
                    1: {'mimetype': 'audio/aac', 'version': '(:unap)'},
                    2: {'mimetype': 'video/mp4', 'version': '(:unap)'}
                }
            ),
            RECOMMENDED
        ),
        # Otherwise recommended but one acceptable stream
        (
            FakeScraper(
                'video/mp4', '(:unap)',
                {
                    0: {'mimetype': 'video/mp4', 'version': '(:unap)'},
                    1: {'mimetype': 'video/mp4', 'version': '(:unap)'},
                    2: {'mimetype': 'audio/mpeg', 'version': '2'}
                }
            ),
            ACCEPTABLE
        ),
        # Contains a stream that is only accepted to bit-level preservation
        (
            FakeScraper(
                'video/quicktime', '(:unap)',
                {
                    0: {'mimetype': 'video/quicktime', 'version': '(:unap)'},
                    1: {'mimetype': 'audio/aac', 'version': '(:unap)'},
                    2: {'mimetype': 'video/x.fi-dpres.prores',
                        'version': '(:unap)'}
                }
            ),
            BIT_LEVEL_WITH_RECOMMENDED
        ),
        # Contains unacceptable stream
        (
            FakeScraper(
                'video/mj2', '(:unap)',
                {
                    0: {'mimetype': 'video/mj2', 'version': '(:unap)'},
                    1: {'mimetype': 'audio/unacceptable', 'version': '0'},
                }
            ),
            UNACCEPTABLE
        ),
    ]
)
def test_container_streams_grader(scraper, expected_grade):
    """Test that ContainerStreamsGrader gives expected grade for file."""
    grader = ContainerStreamsGrader(scraper)
    assert grader.grade() == expected_grade
