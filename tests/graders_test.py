"""Tests for graders."""
import pytest

from file_scraper.defaults import ACCEPTABLE, RECOMMENDED, UNACCEPTABLE
from file_scraper.graders import Grader, TextGrader


@pytest.mark.parametrize(
    ('mimetype', 'version', 'expected_grade'),
    [
        ('application/pdf', 'A-1a', RECOMMENDED),
        ('application/pdf', '1.2', ACCEPTABLE),
        ('application/pdf', 'foo', UNACCEPTABLE)
    ]
)
def test_grader(mimetype, version, expected_grade):
    """Test that Grader gives expected grade for file."""
    grader = Grader(mimetype, version, streams={})
    assert grader.grade() == expected_grade


@pytest.mark.parametrize(
    ('mimetype', 'version', 'charset', 'expected_grade'),
    [
        ('text/csv', '(:unap)', 'UTF-8', RECOMMENDED),
        ('text/csv', 'foo', 'UTF-8', UNACCEPTABLE),
        ('text/csv', '(:unap)', 'foo', UNACCEPTABLE)
    ]
)
def test_text_grader(mimetype, version, charset, expected_grade):
    """Test that TextGrader gives expected grade for file."""
    grader = TextGrader(mimetype,
                        version,
                        streams={0: {'charset': charset}})
    assert grader.grade() == expected_grade
