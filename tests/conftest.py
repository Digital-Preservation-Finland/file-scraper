"""Configure py.test default values and functionality."""
from __future__ import annotations

import os
from typing import Callable
import file_scraper.shell
import pytest
from file_scraper.base import BaseExtractor

from tests.common import Correct, partial_message_included

# Pylint does not understand pytest fixtures
# pylint: disable=redefined-outer-name


@pytest.fixture(autouse=True)
def set_config(monkeypatch):
    """
    Set the correct environment variable for tests
    The content of environment variables are defined in the config folder.
    """
    monkeypatch.setenv("FILE_SCRAPER_CONFIG",
                       "tests/config/file-scraper-duplicate.conf")


@pytest.fixture(scope="function")
def fido_cache_halting_file(tmpdir):
    """File that originally halted the FidoReader due to caching mistake.

    It should not take as long as Fido to identify or detect the file. Before
    due to caching mistake, old FidoDetector would take near 10 seconds to
    process this file while Fido processed it within 3 seconds.
    """
    filepath = os.path.join(tmpdir, 'freeze_fido.bin')
    with open(filepath, 'wb') as out_file:
        out_file.write(b"\xff\xfb\x10" * 1000)

    return filepath


@pytest.fixture(scope="function")
def evaluate_extractor() -> Callable[
    [BaseExtractor, Correct, bool, str | None], None
]:
    """Provide a function to evaluate between extractor- and correct-instance's
    values.
    """

    def _func(
        extractor: BaseExtractor,
        correct: Correct,
        eval_output: bool = True,
        exp_extractor_cls: str | None = None,
    ) -> None:
        """Make common asserts between initialized extractor and correct
            instance.

        :param extractor: Extractor instance obj.
        :param correct: Correct instance obj.
        :param eval_output: True to also evaluate the stdin and stderr between
            extractor and correct.
        :param exp_extractor_cls: What is the actual expected extractor
        classname. If None, will assume default type(extractor).__name__
        """
        if exp_extractor_cls is None:
            exp_extractor_cls = type(extractor).__name__

        for stream_index, stream_metadata in correct.streams.items():
            if extractor._predefined_mimetype:
                assert extractor.streams, (
                    "Empty stream list resulted, possibly unexpected"
                    "predefined mimetype: "
                    + str(extractor._predefined_mimetype)
                )
            else:
                assert extractor.streams, "Streams list can't be empty"
            extracted_metadata = extractor.streams[stream_index]
            for key, value in stream_metadata.items():
                assert getattr(extracted_metadata, key)() == value, (
                    f"Expected {key} to have value '{value}', got "
                    f"'{getattr(extracted_metadata, key)()}' instead"
                )

        assert extractor.info()["class"] == exp_extractor_cls
        assert extractor.well_formed == correct.well_formed

        if eval_output:
            assert partial_message_included(
                correct.stdout_part, extractor.messages()
            )
            assert partial_message_included(
                correct.stderr_part, extractor.errors()
            )

    return _func


@pytest.fixture(scope="function")
def patch_shell_attributes_fx(monkeypatch):
    """Monkeypatch Shell attributes"""
    monkeypatch.setattr(file_scraper.shell.Shell, "returncode", -1)
    monkeypatch.setattr(file_scraper.shell.Shell, "stdout", "")
    monkeypatch.setattr(file_scraper.shell.Shell, "stderr", "")
