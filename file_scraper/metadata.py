"""Metadata collection.

- provide metadata decorator which should be used in each MetaModel which
  will be included in the file-scraper output.
- merge streams from multiple MetaModels into one list of streams.
"""
from __future__ import annotations

from collections.abc import Iterable
from itertools import chain
from typing import Any, Protocol, TYPE_CHECKING

from file_scraper.exceptions import SkipElementException
from file_scraper.defaults import COMPATIBLE_ENCODINGS
from file_scraper.logger import LOGGER

if TYPE_CHECKING:
    from file_scraper.base import BaseMeta


class MetadataMethod(Protocol):
    """Protocol for type hinting metadata methods."""

    is_metadata: bool
    __name__: str

    def __call__(self) -> Any: ...


COMPATIBLE_VERSIONS = {
    # JPEG JFIF versions are compatible with EXIF versions
    # TODO: Add all versions here.
    "2.2.1": ["1.01"],
    "2.2": ["1.01"],
    # Some PDF versions are compatible with PDF-A versions
    # TODO: The PDF version compatibility lists have been generated
    # based on out test files. Check that these versions actually should
    # be compatible, and add missing versions!
    "A-1a": [
        # valid_A-1a.pdf
        # valid_A-1a_invalid_resource_name.pdf
        "1.4",
        # valid_A-1a_root_1.6.pdf
        "1.6",
        # valid_A-1a_root_1.7.pdf
        "1.7"
    ],
    "A-1b": [
        # valid_A-1b_root_1.7.pdf
        "1.7"
    ],
    "A-2b": [
        # valid_A-2b.pdf
        "1.7",
    ],
    "A-2u": [
        # valid_A-2u_root_1.5.pdf
        "1.5"
    ],
    "A-3b": [
        # valid_A-3b_no_file_extension
        # valid_A-3b.pdf
        "1.7",
    ],
}


def generate_metadata_dict(
    extraction_results: list[list[BaseMeta]],
    # TODO: Why overwrite is a parameter? Shouldn't it be always have
    # the same value?
    overwrite: Iterable[str | None],
    mimetype: str,
    version: str,
    charset: str | None,
) -> tuple[dict, list[str]]:
    """
    Generate a metadata dict from the given extraction results.

    The resulting dict contains the metadata of each stream as a dict,
    retrievable by using the index of the stream as a key. The indexing
    starts from zero. In case of conflicting values, the error messages
    are reported back to the scraper.

    :param extraction_results: A list containing lists of all metadata methods,
        methods of a single extractor in a single list. E.g.
        [[extractor1_stream1, extractor1_stream2],
        [extractor2_stream1, extractor2_stream2]]
    :param overwrite: A list of values that can be overwritten.
    :param mimetype: mimetype of the file
    :param version: format version of the file
    :returns: A tuple of (a dict containing the metadata of the file,
        metadata of each stream in its own dict. E.g.
        {
            0: {'mimetype': 'video/h264',
                'index': 1,
                'frame_rate': '30', ...},
            1: {'mimetype': 'audio/aac',
                'index': 2,
                'audio_data_encoding': 'AAC', ...}
        },
        and a list of error messages due to conflicting values). If there are
        no extration results, the dict and list are empty.

    """
    # TODO: Some kind of predefined streams object parameter could be
    # used instead of separate, mimetype, version and charset.
    streams = {
        # TODO: The detected version could always be used, if detectors
        # would always produce good result. Currently it is used only
        # when it is needed to resolve conflicts between extractors.
        0: {
            "mimetype": mimetype,
            "version": version if version in COMPATIBLE_VERSIONS else None,
        }
    }
    if charset:
        streams[0]["charset"] = charset
    conflicts = []

    # Iterate methods to generate metadata dict
    for model in chain.from_iterable(extraction_results):
        stream_index = model.index()
        current_stream = streams.setdefault(stream_index, {})

        # Check that mimetype of the stream matches
        old_mimetype = current_stream.get("mimetype")
        if old_mimetype not in overwrite \
                and model.mimetype() not in overwrite \
                and old_mimetype != model.mimetype():
            conflicts.append(
                f"The stream has conflicting mimetype {model.mimetype()}, "
                "so it is omitted."
            )
            continue
        if model.mimetype() not in overwrite \
                or old_mimetype in overwrite:
            current_stream["mimetype"] = model.mimetype()

        # Check that the version of the stream matches or is compatible
        old_version = current_stream.get("version")
        if old_version in overwrite:
            current_stream["version"] = model.version()
        elif old_version == model.version() or model.version() in overwrite:
            # No need to update
            pass
        elif model.version() in COMPATIBLE_VERSIONS.get(old_version, []):
            # No need to update, but log a debug message
            LOGGER.debug(
                "Detected version %s which is compatible with %s",
                model.version(), old_version
            )
        else:
            conflicts.append(
                f"The stream has conflicting version {model.version()}, "
                "so it is omitted."
            )
            continue

        # Check that the charset matches predefined charset
        if hasattr(model, "charset"):
            # TODO: Only the first stream should have charset, and it
            # should have been detected by detectors. However, if user
            # has predefined the file as text file, and the file is
            # something else, the charset might not be "(:unav)". We
            # should at least add such test case, if we don't already
            # have it.
            old_charset = current_stream["charset"]
            if model.charset() == old_charset\
                    or model.charset() in overwrite:
                # No need to update charset
                pass
            elif model.charset() in COMPATIBLE_ENCODINGS.get(old_charset, []):
                LOGGER.debug(
                    "Extractor detected charset %s, which is "
                    "compatible with %s",
                    model.charset(), old_charset
                )
            else:
                LOGGER.debug(
                    "The stream has conflicting charset %s", model.charset()
                )
                conflicts.append(
                    f"The stream has conflicting charset {model.charset()}"
                )

        # The mimetype and version match to previous models, so we can
        # merge rest of the metadata
        for method in model.iterate_metadata_methods():
            name = method.__name__
            if name in ["mimetype", "version", "charset"]:
                continue
            try:
                new_value = method()
            except SkipElementException:
                # happens when the method is not to be indexed
                # TODO: Why does the method then exist? See TPASPKT-1577
                continue

            if name not in current_stream:
                # Previous models did not define this key
                current_stream[name] = new_value
                continue
            old_value = current_stream[name]
            if old_value == new_value:
                # This model agrees with previous models
                continue
            if old_value in overwrite:
                # The previous models found overwritable value
                current_stream[name] = new_value
                continue
            if new_value in overwrite:
                # The current model found overwritebale value which
                # conflicts with the value from previous models.
                continue

            # The values are incompatible, so either there is something
            # wrong in the file, or there is bug in file-scraper.
            conflicts.append(
                # TODO: The value could be produced also by detector, or
                # it could be defined by user, so this error message
                # could be misleading in some cases.
                f"The Extractors produced conflicting values for {name}:"
                f" {old_value} and {new_value}"
            )

        # TODO: Instead of logging the result after merging streams
        # (current_stream), it would be more useful to log the stream
        # that was merged (model). See TPASPKT-1570.
        LOGGER.debug(
            "Scraper result %s merged to stream: %s", model, current_stream
        )

    return streams, conflicts
