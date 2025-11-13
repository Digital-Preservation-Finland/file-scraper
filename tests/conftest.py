"""Configure py.test default values and functionality."""
from __future__ import annotations

import os
from typing import Callable

import file_scraper.shell
import pytest
from file_scraper.base import BaseExtractor, BaseMeta


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


class Meta1(BaseMeta):
    """
    Metadata class for testing generate_metadata_dict().

    This metadata class is used to test merging two metadata models with
    identical indices. This and Meta2 contain a variety of compatible and
    conflicting metadata methods that allow testing both important values
    and LOSE dict.
    """

    @BaseMeta.metadata()
    def index(self):
        """Return 0: this metadata class will be merged with Meta2."""
        return 0

    @BaseMeta.metadata()
    def mimetype(self):
        """Same MIME type as Meta2 has."""
        return "mime"

    @BaseMeta.metadata()
    def version(self):
        """Same version as Meta2 has."""
        return 1.0

    @BaseMeta.metadata()
    def stream_type(self):
        """Same stream type as Meta2 has."""
        return "binary"

    @BaseMeta.metadata()
    def key1(self):
        """
        This value conflicts with Meta2 and neither is important.

        This method can be used to test the LOSE dict.
        """
        return "value1-1"

    @BaseMeta.metadata()
    def key2(self):
        """This value is compatible with Meta2."""
        return "value2"

    @BaseMeta.metadata()
    def key3(self):
        """This value conflicts with Meta2 and the Meta2 value is important."""
        return "key1-3"

    @BaseMeta.metadata(important=True)
    def key4(self):
        """This value conflicts with Meta2 and this value is important."""
        return "importantvalue"


class Meta2(BaseMeta):
    """
    Metadata class for testing generate_metadata_dict().

    This metadata class is used to test merging two metadata models with
    identical indices. This and Meta1 contain a variety of compatible and
    conflicting metadata methods that allow testing both important values
    and LOSE dict.
    """

    @BaseMeta.metadata()
    def index(self):
        """Return 0: this metadata class will be merged with Meta1."""
        return 0

    @BaseMeta.metadata()
    def mimetype(self):
        """Same MIME type as Meta1 has."""
        return "mime"

    @BaseMeta.metadata()
    def version(self):
        """Same version as Meta1 has."""
        return 1.0

    @BaseMeta.metadata()
    def stream_type(self):
        """Same stream type as Meta1 has."""
        return "binary"

    @BaseMeta.metadata()
    def key1(self):
        """
        This value conflicts with Meta1 and neither is important.

        This method can be used to test the LOSE dict.
        """
        return "value2-1"

    @BaseMeta.metadata()
    def key2(self):
        """This value is compatible with Meta1."""
        return "value2"

    @BaseMeta.metadata(important=True)
    def key3(self):
        """This value conflicts with Meta1 and this value is important."""
        return "key2-3"

    @BaseMeta.metadata()
    def key4(self):
        """This value conflicts with Meta1 and the Meta1 value is important."""
        return "unimportant value"


class Meta3(BaseMeta):
    """
    Metadata class for testing generate_metadata_dict().

    This metadata class is used to test that metadata models with different
    indices yield different streams in the metadata dict. Values of MIME type,
    version, stream_type or other metadata fields do not need to match the
    other streams.
    """

    @BaseMeta.metadata()
    def index(self):
        """Return stream index"""
        return 1

    @BaseMeta.metadata()
    def mimetype(self):
        """Return MIME type"""
        return "anothermime"

    @BaseMeta.metadata()
    def version(self):
        """Return version"""
        return 2

    @BaseMeta.metadata()
    def stream_type(self):
        """Return stream type"""
        return "audio"

    @BaseMeta.metadata()
    def key1(self):
        """Return metadata"""
        return "value1"

    @BaseMeta.metadata()
    def key2(self):
        """Return metadata"""
        return "value2"


class Meta4(BaseMeta):
    """
    Conflicting important value with Meta1(), where key4() is also important.
    """

    @BaseMeta.metadata()
    def mimetype(self):
        """Same MIME type as Meta1 has."""
        return "mime"

    @BaseMeta.metadata()
    def version(self):
        """Same version as Meta1 has."""
        return 1.0

    @BaseMeta.metadata()
    def stream_type(self):
        """Same stream type as Meta1 has."""
        return "binary"

    @BaseMeta.metadata(important=True)
    def key4(self):
        """Return metadata, which will conflict with Meta1()"""
        return "conflictingvalue"


class Meta5(BaseMeta):
    """
    Identical metadata with Meta1. Used for testing that results
    can be merged to scraper.stream without conflicts.
    """
    @BaseMeta.metadata()
    def index(self):
        """Return 0: this metadata class will be merged with Meta1."""
        return 0

    @BaseMeta.metadata()
    def mimetype(self):
        """Same MIME type as Meta1 has."""
        return "mime"

    @BaseMeta.metadata()
    def version(self):
        """Same version as Meta1 has."""
        return 1.0

    @BaseMeta.metadata()
    def stream_type(self):
        """Same stream type as Meta1 has."""
        return "binary"


@pytest.fixture(scope="function")
def meta_class_fx():
    """Fixture to return Metadata classes for tests."""
    def _meta_class(class_name):
        """Returns a Metadata class based on the class_name."""
        if class_name == 'meta2':
            return Meta2()
        if class_name == 'meta3':
            return Meta3()
        if class_name == 'meta4':
            return Meta4()
        if class_name == 'meta5':
            return Meta5()
        return Meta1()

    return _meta_class
