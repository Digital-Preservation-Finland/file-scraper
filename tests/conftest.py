"""Configure py.test default values and functionality."""
from __future__ import unicode_literals

import tempfile
import shutil

import pytest
from tests.common import partial_message_included


@pytest.yield_fixture(scope="function")
def testpath():
    """
    Creates temporary directory and clean up after testing.

    :yields: Path to temporary directory
    """
    temp_path = tempfile.mkdtemp(prefix="tests.testpath.")
    yield temp_path
    shutil.rmtree(temp_path)


@pytest.fixture(scope="function")
def evaluate_scraper():
    """Provide a function to evaluate between scraper- and correct-instance's
    values.
    """

    def _func(scraper, correct, eval_output=True, exp_scraper_cls=None):
        """Make common asserts between initialized scraper and correct
            instance.

        :param scraper: Scraper instance obj.
        :param correct: Correct instance obj.
        :param eval_output: True to also evaluate the stdin and stderr between
            scraper and correct.
        :param exp_scraper_cls: What is the actual expected scraper class name.
            If None, will assume default type(scraper).__name__
        """
        if exp_scraper_cls is None:
            exp_scraper_cls = type(scraper).__name__

        for stream_index, stream_metadata in correct.streams.items():
            scraped_metadata = scraper.streams[stream_index]
            for key, value in stream_metadata.items():
                assert getattr(scraped_metadata, key)() == value, (
                    "Expected {} to have value '{}', got '{}' instead".format(
                        key, value, getattr(scraped_metadata, key)()
                    )
                )

        assert scraper.info()["class"] == exp_scraper_cls
        assert scraper.well_formed == correct.well_formed

        if eval_output:
            assert partial_message_included(correct.stdout_part,
                                           scraper.messages())
            assert partial_message_included(correct.stderr_part,
                                           scraper.errors())

    return _func
