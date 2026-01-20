"""
Tests for the metadata module.

These are the requirements for the metadata functions:
requirements:
    - strip_zeros
        - When there are no zeros to be stripped in the input, the output is
          identical.
        - One or more trailing zeros from the decimal part are removed from
          the returned string.
        - Non-trailing zeros in the decimal part are not affected.
        - If nothing is left in the decimal part, decimal point is also removed
          from the returned string.
        - Trailing zeros in the integer part are not affected.
        - Leading zeros are not affected.
        - Underscores in the input do not affect the stripping, e.g.
          "1_000_000" is not altered but for "1_234_000.000_000", "1_234_000"
          is returned.
    - _merge_functions_to_stream
        - Value returned by the given metadata method is or is not added to
          the given metadata dict with the method name as the key under the
          following conditions:
            - If the key is not present, a new key is always added whether the
              value is in lose dict or not.
            - If the key is already present but not important and the new
              method is important, the old value is replaced by the new one.
            - If the old value is important and the new one is not, the old
              value is not replaced.
            - If the old value is present in the lose list, the new value
              replaces it whether the new one is important or not.
            - If the new value is present in the lose list and the old one is
              not, the old value is kept.
            - When old and new value are identical, no exceptions are raised
              and the value is kept as is.
            - If old and new values differ aind neither is important nor in
              lose, ValueError is raised.
            - If old and new values differ and both are important, ValueError
              is raised.
        - If the method is important, the entry is also added to the importants
          dict.
    - merge_normal_conflict
        - Adding non-important metadata causes conflict error when another
          value already exists in stream.
    - merge_important_conflict
        - Adding important value causes conflict error when another important
          value already exists in stream.
    - fill_importants
        - Important values are resulted as important
        - Lose values marked as important are not important
    - generate_metadata_dict
        - A dict with metadata method names as keys and return values as values
          is returned with priority of conflicting values determined correctly
          based on the given lose list and importantness of the methods.
        - Indexes of the streams start from 0 and correspond to the keys
          in the outer dict.
        - If the lose list contains a value some method marks as important, an
          OverlappingLoseAndImportantException is raised.
"""

import pytest

from file_scraper.base import BaseMeta
from file_scraper.metadata import generate_metadata_dict


class Meta1(BaseMeta):
    """
    Metadata class for testing generate_metadata_dict().

    This class is associated with Meta2.

    This metadata class is used to test merging two metadata models with
    identical indices. This and Meta2 contain a variety of compatible and
    conflicting metadata methods.
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
        return "1.0"

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
        return "value1-3"

    @BaseMeta.metadata()
    def key4(self):
        """This value conflicts with Meta2 and this value is important."""
        return "value4"


class Meta2(BaseMeta):
    """
    Metadata class for testing generate_metadata_dict().

    This class is associated with Meta1

    This metadata class is used to test merging two metadata models with
    identical indices. This and Meta1 contain a variety of compatible and
    conflicting metadata methods.
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
        return "1.0"

    @BaseMeta.metadata()
    def stream_type(self):
        """Same stream type as Meta1 has."""
        return "binary"

    @BaseMeta.metadata()
    def key1(self):
        """
        This value conflicts with Meta1.

        This method can be used to test overwriting.
        """
        return "value2-1"

    @BaseMeta.metadata()
    def key2(self):
        """This value is compatible with Meta1."""
        return "value2"

    @BaseMeta.metadata()
    def key3(self):
        """This value conflicts with Meta1"""
        return "value2-3"

    @BaseMeta.metadata()
    def key4(self):
        """This value conflicts with Meta1"""
        return "conflicting value"


class Meta3(BaseMeta):
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
        return "1.0"

    @BaseMeta.metadata()
    def stream_type(self):
        """Same stream type as Meta1 has."""
        return "binary"


class Meta4(BaseMeta):
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


def test_generate_metadata_dict():
    """Test generating metadata dict using the metadata objects.

    Check that result contains expected metata, and that conflicts were
    not found.
    """
    results = [[Meta1()], [Meta1()]]
    (metadata_dict, conflicts) \
        = generate_metadata_dict(
            extraction_results=results,
            overwrite=[None],
            mimetype="mime",
            version="1.0",
            charset=None,
        )

    # Check that result contains expected metadata
    assert metadata_dict == {
        0: {
            "index": 0,
            "key1": "value1-1",
            "key2": "value2",
            "key3": "value1-3",
            "key4": "value4",
            "mimetype": "mime",
            "version": "1.0",
            "stream_type": "binary",
        },
    }

    # There should not be conflicts
    assert conflicts == []


@pytest.mark.parametrize(
    ("meta_classes", "lose", "expected_conflicts"),
    [
        # Only None should be overwritten
        (
            [Meta1, Meta2, Meta4],
            [None],
            [
                "The Extractors produced conflicting values for key1: "
                "value1-1 and value2-1",
                "The Extractors produced conflicting values for key3: "
                "value1-3 and value2-3",
                "The Extractors produced conflicting values for key4: "
                "value4 and conflicting value",
            ],
        ),
        # Overwriting "value2-1" is allowed, so it should not cause
        # conflict
        (
            [Meta1, Meta2, Meta4],
            [None, "value2-1"],
            [
                "The Extractors produced conflicting values for key3: "
                "value1-3 and value2-3",
                "The Extractors produced conflicting values for key4: "
                "value4 and conflicting value",
            ],
        ),
    ],
)
def test_generate_metadata_dict_conflicts(
    meta_classes, lose, expected_conflicts
):
    """Test merging conflicting metadata models.

    Check that expected error messages are produced.
    """
    results = [[meta_class()] for meta_class in meta_classes]
    (_metadata_dict, conflicts) \
        = generate_metadata_dict(
            extraction_results=results,
            overwrite=lose,
            mimetype="mime",
            version="1.0",
            charset=None,
        )

    assert conflicts == expected_conflicts


def test_generate_metadata_mimetype_conflict():
    """Test merging streams with conflicting mimetype or version.

    If a stream has conflicting mimetype or version, none of the
    metadata should be merged to the result.
    """

    class ConflictingMimetypeMeta(Meta1):

        @BaseMeta.metadata()
        def mimetype(self):
            return "wrong-mime"

        @BaseMeta.metadata()
        def extrakey(self):
            return "value-of-extrakey"

    results = [[Meta1()], [ConflictingMimetypeMeta()]]
    (metadata_dict, conflicts) \
        = generate_metadata_dict(
            extraction_results=results,
            overwrite=[None],
            mimetype="mime",
            version="1.0",
            charset=None,
        )

    assert conflicts == ["The stream has conflicting mimetype "
                         "wrong-mime, so it is omitted."]
    assert "extrakey" not in metadata_dict[0]
    assert "extrakey" not in metadata_dict[0]


def test_generate_metadata_version_conflict():
    """Test merging streams with conflicting mimetype or version.

    If a stream has conflicting mimetype or version, none of the
    metadata should be merged to the result.
    """

    class ConflictingMimetypeMeta(Meta1):

        @BaseMeta.metadata()
        def version(self):
            return "wrong-version"

        @BaseMeta.metadata()
        def extrakey(self):
            return "value-of-extrakey"

    results = [[Meta1()], [ConflictingMimetypeMeta()]]
    (metadata_dict, conflicts) \
        = generate_metadata_dict(
            extraction_results=results,
            overwrite=[None],
            mimetype="mime",
            version="1.0",
            charset=None,
        )

    assert conflicts == ["The stream has conflicting version "
                         "wrong-version, so it is omitted."]

    # The extrakey should not be added to metadata_dict, because the
    # conflicting stream is omitted
    assert "extrakey" not in metadata_dict[0]
