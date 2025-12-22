"""
Metadata collection.
 - provide metadata decorator which should be used in each MetaModel which
   will be included in the file-scraper output.
 - merge streams from multiple MetaModels into one list of streams.
"""
from __future__ import annotations

from collections.abc import Iterable
from itertools import chain
from typing import Any, Protocol, TYPE_CHECKING

from file_scraper.exceptions import SkipElementException
from file_scraper.logger import LOGGER

if TYPE_CHECKING:
    from file_scraper.base import BaseMeta


class MetadataMethod(Protocol):
    """Protocol for type hinting metadata methods."""

    is_metadata: bool
    __name__: str

    def __call__(self) -> Any: ...


def _merge_functions_to_stream(
    stream: dict[str, str],
    method: MetadataMethod,
    overwrite: Iterable[str | None],
) -> None:
    """
    Merges the methods in-place into the stream dictionary.

    Adds item 'method.__name__: method' into the stream dict.

    If the stream dict already contains an entry with method.__name__ as the
    key, the value for the key is checked against the overwrite list and will
    be replaced if it exists in it. Otherwise the value writing has failed and
    a ValueError will be raised.

    :param stream: A dict representing the metadata of a single stream.
        The content of each key must be a function to determine the origin
        of the data. The origin will be used to give good ValueError messages.
        An example of the dict:
        `
        {
            "index": <function which returns index>,
            "mimetype": <function which returns mimetype>,
            "width": <function which returns width>
        }
        `
        The 'index' key
        is required for the dict!
    :param method: A metadata method which returns the right value for
        the metadata.
    :param overwrite: A list of values that can be overwritten and prevent
        writing the these values to the stream.

    :raises: ValueError if the value failed merging, the most common reason is
        that the value was already written to the stream by another function.
    """
    method_name = method.__name__
    model_name = method.__self__.__class__.__name__
    method_value = method()

    if method_name not in stream:
        stream[method_name] = method
        return
    stream_method_value = stream[method_name]()
    if method_value in overwrite:
        return
    if stream_method_value == method_value:
        return
    if stream_method_value in overwrite:
        stream[method_name] = method
        return

    stream_model_name = stream[method_name].__self__.__class__.__name__
    raise ValueError(
        f"Failed to merge the metadata '{method_name}' from the model "
        f"'{model_name}' with a value of '{method_value}' to the stream. "
        f"The existing stream metadata was produced by the model "
        f"'{stream_model_name}' with a value '{stream_method_value}'."
    )


def generate_metadata_dict(
    extraction_results: list[list[BaseMeta]], overwrite: Iterable[str | None]
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
    streams = {}
    conflicts = []

    # Iterate methods to generate metadata dict
    for model in chain.from_iterable(extraction_results):
        stream_index = model.index()
        current_stream = streams.setdefault(stream_index, {})

        for method in model.iterate_metadata_methods():
            try:
                _merge_functions_to_stream(current_stream, method, overwrite)
            # In case of conflicting values, append the error message
            except SkipElementException:
                # happens when the method is not to be indexed
                continue
            except ValueError as err:
                conflicts.append(str(err))
        LOGGER.debug(
            "Scraper result %s merged to stream: %s", model, current_stream
        )
    # Change the function reference into a result for each stream
    for index, stream in streams.items():
        for key, method in stream.items():
            streams[index][key] = method()

    return streams, conflicts
