"""Tests for file_scraper.metadata."""

from file_scraper.base import BaseMeta
from file_scraper.metadata import generate_metadata_dict


class Meta1(BaseMeta):
    """Metadata class for testing generate_metadata_dict()."""

    @BaseMeta.metadata()
    def index(self):
        """Return 0."""
        return 0

    @BaseMeta.metadata()
    def mimetype(self):
        """Return hard-coded mimetype."""
        return "mime"

    @BaseMeta.metadata()
    def version(self):
        """Return hard-coded version."""
        return "1.0"

    @BaseMeta.metadata()
    def key1(self):
        """Return hard-coded generic metadata."""
        return "value1-1"


def test_generate_metadata_dict():
    """Test generating metadata dict using the metadata objects.

    Check that result contains expected metata, and that conflicts were
    not found.
    """
    streams = {
        0: Meta1().to_dict()
    }
    conflicts = generate_metadata_dict(
        streams,
        [Meta1()],
    )

    # streams should not have changed
    assert streams == {
        0: Meta1().to_dict()
    }

    # There should not be conflicts
    assert conflicts == []


def test_generate_metadata_dict_conflicts():
    """Test merging conflicting metadata models.

    Check that expected error messages are produced.
    """
    class ConflictingMimetypeMeta(Meta1):

        @BaseMeta.metadata()
        def key1(self):
            return "conflicting-value"

        @BaseMeta.metadata()
        def key2(self):
            return "another-value"

    streams = {
        0: Meta1().to_dict(),
    }
    conflicts = generate_metadata_dict(
        streams,
        [ConflictingMimetypeMeta()],
    )

    assert conflicts == [
        "The Extractors produced conflicting values for key1: "
        "value1-1 and conflicting-value",
    ]

    # The merged dict should contain new values values from the
    # ConflictingMimetypeMeta, but the conflicting-value should not
    # overwrite the original value
    expected_result = {0: Meta1().to_dict()}
    expected_result[0]["key2"] = "another-value"
    assert streams == expected_result


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

    streams = {
        0: Meta1().to_dict(),
    }
    conflicts = generate_metadata_dict(
        streams,
        [ConflictingMimetypeMeta()],
    )

    assert conflicts == ["The stream has conflicting mimetype "
                         "wrong-mime, so it is omitted."]
    assert "extrakey" not in streams[0]
    assert "extrakey" not in streams[0]


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

    streams = {
        0: Meta1().to_dict(),
    }
    conflicts = generate_metadata_dict(
        streams,
        [ConflictingMimetypeMeta()],
    )

    assert conflicts == ["The stream has conflicting version "
                         "wrong-version, so it is omitted."]

    # The extrakey should not be added to metadata_dict, because the
    # conflicting stream is omitted
    assert "extrakey" not in streams[0]
