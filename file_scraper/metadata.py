"""Metadata collection.

- provide metadata decorator which should be used in each MetaModel which
  will be included in the file-scraper output.
- merge streams from multiple MetaModels into one list of streams.
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Any, Protocol

from file_scraper.defaults import (
    COMPATIBLE_ENCODINGS,
    COMPATIBLE_MIMETYPES,
    COMPATIBLE_VERSIONS,
    UNAV,
)
from file_scraper.logger import LOGGER

if TYPE_CHECKING:
    from file_scraper.base import BaseMeta

LOSE = [None, UNAV]


class MetadataMethod(Protocol):
    """Protocol for type hinting metadata methods."""

    is_metadata: bool
    __name__: str

    def __call__(self) -> Any: ...


def generate_metadata_dict(
    streams,
    new_streams: list[BaseMeta]
) -> list[str]:
    """Merge metadata from models streams dictinary.

    The streams dictionary is a nested dictionary that maps each stream
    index to a dictionary of stream properties, for example:

    {
        0: {'mimetype': 'video/h264',
            'index': 0,
            'frame_rate': '30', ...},
        1: {'mimetype': 'audio/aac',
            'index': 1,
            'audio_data_encoding': 'AAC', ...}
    },

    :param streams: The streams dict
    :param new_streams: list of metadata models to be merged
    :returns: list of error messages generated from conflicts
    """
    conflicts = []

    for model in new_streams:
        current_stream = streams.setdefault(model.index(), {})

        compatible_mimetypes \
            = COMPATIBLE_MIMETYPES.get(current_stream.get("mimetype"), []) \
            + LOSE \
            + [current_stream.get("mimetype")]

        compatible_versions \
            = COMPATIBLE_VERSIONS.get(
                current_stream.get("mimetype"), {}
            ).get(
                current_stream.get("version"), []
            ) \
            + LOSE \
            + [current_stream.get("version")]

        # Check that mimetype and version of the model are compatible
        # with the previously merged models.
        if current_stream.get("mimetype") not in LOSE \
                and model.mimetype() not in compatible_mimetypes:
            conflict = ("The stream has conflicting mimetype "
                        f"{model.mimetype()}, so it is omitted.")
            conflicts.append(conflict)
            LOGGER.debug(conflict)
            continue
        if current_stream.get("version") not in LOSE \
                and model.version() not in compatible_versions:
            conflict = ("The stream has conflicting version "
                        f"{model.version()}, so it is omitted.")
            conflicts.append(conflict)
            LOGGER.debug(conflict)
            continue

        # Merge stream method by method
        compatible_encodings \
            = COMPATIBLE_ENCODINGS.get(
                current_stream.get("charset"), []
            ) \
            + LOSE \
            + [current_stream.get("version")]

        compatible_values = {
            "mimetype": compatible_mimetypes,
            "version": compatible_versions,
            "charset": compatible_encodings,
        }
        for name, new_value in model.to_dict().items():
            old_value = current_stream.get(name)
            if old_value in LOSE:
                # The previous models found overwritable value
                current_stream[name] = new_value
                continue
            if old_value == new_value:
                # This model agrees with previous models
                continue
            if new_value in LOSE:
                # The current model found overwritable value which
                # conflicts with the value from previous models.
                continue
            if new_value in compatible_values.get(name, []):
                LOGGER.debug(
                    "Extractor detected %s %s, which is "
                    "compatible with %s", name, new_value, old_value
                )
                continue
            # The values are incompatible, so either there is something
            # wrong in the file, or there is bug in file-scraper.
            conflicts.append(
                f"The Extractors produced conflicting values for {name}:"
                f" {old_value} and {new_value}"
            )

        # TODO: Instead of logging the result after merging streams
        # (current_stream), it would be more useful to log the stream
        # that was merged (model). See TPASPKT-1570.
        LOGGER.debug(
            "Scraper result %s merged to stream: %s", model, current_stream
        )

    return conflicts
