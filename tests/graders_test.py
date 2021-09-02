"""Tests for graders."""
from collections import namedtuple

import pytest
from file_scraper.defaults import ACCEPTABLE, RECOMMENDED, UNACCEPTABLE
from file_scraper.graders import MIMEGrader, TextGrader

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
