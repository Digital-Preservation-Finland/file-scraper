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

from dpres_file_formats.defaults import UnknownValue as Unk

from file_scraper.exceptions import SkipElementException
from file_scraper.logger import LOGGER

if TYPE_CHECKING:
    from file_scraper.base import BaseMeta


class MetadataMethod(Protocol):
    """Protocol for type hinting metadata methods."""

    is_metadata: bool
    is_important: bool
    __name__: str

    def __call__(self) -> Any: ...


def _merge_to_stream(
    stream: dict[str, str],
    method: MetadataMethod,
    lose: Iterable[str | None],
    importants: dict[str, str],
) -> None:
    """
    Merges the results of the method into the stream dict.

    Adds item 'method.__name__: method()' into the stream dict.

    If the stream dict already contains an entry with method.__name__ as the
    key, the given lose and importants are examined:
        - Important values are used unless those are lose values.
        - Values within the lose list are overwritten.
        - If neither entry is important or disposable, a ValueError is raised.

    :param stream: A dict representing the metadata of a single stream. E.g.
        {"index": 0, "mimetype": "image/png", "width": "500"}
    :param method: A metadata method.
    :param lose: A list of values that can be overwritten.
    :param importants: A dict of keys and values that must not be overwritten.
    :raises: ValueError if the old entry in the stream and the value returned
        by the given method conflict but neither is disposable.
    """
    method_name = method.__name__
    method_value = method()

    if method_name not in stream:
        stream[method_name] = method_value
        return
    if method_value in lose:
        return
    if stream[method_name] == method_value:
        return

    if method.is_important:
        LOGGER.debug(
            "Stream metadata field '%s' overwritten with important value: "
            "%s -> %s",
            method_name, stream[method_name], method_value
        )
        stream[method_name] = method_value
    elif method_name in importants:
        return
    elif stream[method_name] in lose:
        stream[method_name] = method_value
    else:
        # Set the value as UNAV and raise ValueError
        existing_value = stream[method_name]
        stream[method_name] = Unk.UNAV
        raise ValueError(
            f"Conflict with values '{existing_value}' and '{method_value}' "
            f"for '{method_name}'.")


def _fill_importants(
    method: MetadataMethod,
    importants: dict[str, str],
    lose: Iterable[str | None],
) -> None:
    """
    Find the important metadata values for a method.

    :param method: A metadata method
    :param importants: A dictionary of important metadata values
    :param lose: List of values which can not be important
    :raises: ValueError if two different important values collide in a
        method.
    """
    try:
        method_name = method.__name__
        method_value = method()
        if method.is_important and method_value not in lose:
            if method_name in importants and \
                    importants[method_name] != method_value:
                raise ValueError(
                    f"Conflict with values '{importants[method_name]}' and "
                    f"'{method_value}' for '{method_name}': both "
                    f"are marked important.")
            importants[method_name] = method_value
    except SkipElementException:
        pass


def generate_metadata_dict(
    extraction_results: list[list[BaseMeta]], lose: Iterable[str | None]
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
    :param lose: A list of values that can be overwritten.
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
    importants = {}

    # First iterate methods to fill the importants dictionary with important
    # metadata values from the extraction results
    for model in chain.from_iterable(extraction_results):
        for method in model.iterate_metadata_methods():
            try:
                _fill_importants(method, importants, lose)
            except ValueError as err:
                conflicts.append(str(err))

    # Iterate methods to generate metadata dict
    for model in chain.from_iterable(extraction_results):
        stream_index = model.index()
        current_stream = streams.setdefault(stream_index, {})

        for method in model.iterate_metadata_methods():
            try:
                _merge_to_stream(current_stream, method, lose, importants)
            except SkipElementException:
                # happens when the method is not to be indexed
                continue
            # In case of conflicting values, append the error message
            except ValueError as err:
                conflicts.append(str(err))
        LOGGER.debug(
            "Scraper result %s merged to stream: %s", model, current_stream
        )

    return streams, conflicts
