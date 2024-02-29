"""Configure py.test default values and functionality."""

import os

import pytest
from tests.common import partial_message_included
import file_scraper.shell
from file_scraper.base import BaseMeta
from file_scraper.utils import metadata

# Pylint does not understand pytest fixtures
# pylint: disable=redefined-outer-name


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
            assert scraper.streams, ("Empty stream list resulted, "
                                     "possibly unexpected predefined "
                                     "mimetype.")
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
    # pylint: disable=no-self-use

    @metadata()
    def index(self):
        """Return 0: this metadata class will be merged with Meta2."""
        return 0

    @metadata()
    def mimetype(self):
        """Same MIME type as Meta2 has."""
        return "mime"

    @metadata()
    def version(self):
        """Same version as Meta2 has."""
        return 1.0

    @metadata()
    def stream_type(self):
        """Same stream type as Meta2 has."""
        return "binary"

    @metadata()
    def key1(self):
        """
        This value conflicts with Meta2 and neither is important.

        This method can be used to test the LOSE dict.
        """
        return "value1-1"

    @metadata()
    def key2(self):
        """This value is compatible with Meta2."""
        return "value2"

    @metadata()
    def key3(self):
        """This value conflicts with Meta2 and the Meta2 value is important."""
        return "key1-3"

    @metadata(important=True)
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
    # pylint: disable=no-self-use

    @metadata()
    def index(self):
        """Return 0: this metadata class will be merged with Meta1."""
        return 0

    @metadata()
    def mimetype(self):
        """Same MIME type as Meta1 has."""
        return "mime"

    @metadata()
    def version(self):
        """Same version as Meta1 has."""
        return 1.0

    @metadata()
    def stream_type(self):
        """Same stream type as Meta1 has."""
        return "binary"

    @metadata()
    def key1(self):
        """
        This value conflicts with Meta1 and neither is important.

        This method can be used to test the LOSE dict.
        """
        return "value2-1"

    @metadata()
    def key2(self):
        """This value is compatible with Meta1."""
        return "value2"

    @metadata(important=True)
    def key3(self):
        """This value conflicts with Meta1 and this value is important."""
        return "key2-3"

    @metadata()
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
    # pylint: disable=no-self-use

    @metadata()
    def index(self):
        """Return stream index"""
        return 1

    @metadata()
    def mimetype(self):
        """Return MIME type"""
        return "anothermime"

    @metadata()
    def version(self):
        """Return version"""
        return 2

    @metadata()
    def stream_type(self):
        """Return stream type"""
        return "audio"

    @metadata()
    def key1(self):
        """Return metadata"""
        return "value1"

    @metadata()
    def key2(self):
        """Return metadata"""
        return "value2"


class Meta4(BaseMeta):
    """
    Conflicting important value with Meta1(), where key4() is also important.
    """
    # pylint: disable=no-self-use

    @metadata()
    def mimetype(self):
        """Same MIME type as Meta1 has."""
        return "mime"

    @metadata()
    def version(self):
        """Same version as Meta1 has."""
        return 1.0

    @metadata()
    def stream_type(self):
        """Same stream type as Meta1 has."""
        return "binary"

    @metadata(important=True)
    def key4(self):
        """Return metadata, which will conflict with Meta1()"""
        return "conflictingvalue"


class Meta5(BaseMeta):
    """
    Identical metadata with Meta1. Used for testing that results
    can be merged to scraper.stream without conflicts.
    """
    # pylint: disable=no-self-use
    @metadata()
    def index(self):
        """Return 0: this metadata class will be merged with Meta1."""
        return 0

    @metadata()
    def mimetype(self):
        """Same MIME type as Meta1 has."""
        return "mime"

    @metadata()
    def version(self):
        """Same version as Meta1 has."""
        return 1.0

    @metadata()
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
