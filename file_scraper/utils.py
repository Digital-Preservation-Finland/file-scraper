"""Utilities for scrapers."""
from __future__ import unicode_literals

import hashlib
import string
import sys
import unicodedata
from itertools import chain

import six

from file_scraper.defaults import UNAV
from file_scraper.exceptions import SkipElementException


def metadata(important=False):
    """
    Decorator for functions scraping metadata.

    :important: True if metadata is important, False otherwise
    :returns: Decorator for function
    """
    def _wrap(func):
        func.is_metadata = True
        func.is_important = important
        return func
    return _wrap


def is_metadata(func):
    """
    Return True if given a function with metadata flag, otherwise False.

    :func: Function to check
    :returns: True if function has metadata flag, False otherwise
    """
    return callable(func) and getattr(func, "is_metadata", False)


def encode_path(filename):
    """
    Encode Unicode filenames.

    :filename: File name no encode
    :returns: Encoded file name
    """
    if isinstance(filename, six.text_type):
        return filename.encode(encoding=sys.getfilesystemencoding())
    elif isinstance(filename, six.binary_type):
        return filename

    raise TypeError("Value is not a (byte) string")


def decode_path(filename):
    """
    Decode Unicode filenames.

    :filename: File name to decode
    :returns: Decoded file name
    """
    return ensure_text(filename, encoding=sys.getfilesystemencoding())


def hexdigest(filename, algorithm="sha1", extra_hash=None):
    """
    Calculte hash of given file.

    :filename: File path
    :algorithm: Hash algorithm. MD5 or SHA variant.
    :extra_hash: Hash to be appended in calculation
    :returns: Calculated hash
    """
    algorithm = algorithm.replace("-", "").lower().strip()
    checksum = hashlib.new(algorithm)
    with open(filename, "rb") as input_file:
        for chunk in iter(lambda: input_file.read(1024 * 1024), b""):
            checksum.update(chunk)
        if extra_hash:
            if isinstance(extra_hash, six.text_type):
                extra_hash = extra_hash.encode("utf-8")
            checksum.update(extra_hash)
    return checksum.hexdigest()


def sanitize_string(dirty_string):
    """
    Strip non-printable control characters from unicode string.

    :dirty_string: String to sanitize
    :returns: Sanitized string
    """
    sanitized_string = "".join(
        char for char in dirty_string if unicodedata.category(char)[0] != "C"
        or char in string.printable)
    return sanitized_string


def iso8601_duration(time):
    """Convert seconds into ISO 8601 duration.

    PT[hours]H[minutes]M[seconds]S format is used with maximum of two decimal
    places used with the seconds. If there are no hours, minutes or seconds,
    that field is not included in the output, unless the total duration is
    zero, at which case "PT0S" is returned.

    >>> iso8601_duration(1.1)
    "PT1.1S"
    >>> iso8601_duration(1.001)
    "PT1S"
    >>> iso8601_duration(60)
    "PT1M"
    >>> iso8601_duration(3601)
    "PT1H1S"
    >>> iso8601_duration(0.001)
    "PT0S"

    :time: Time in seconds
    :returns: ISO 8601 representation of time
    """
    hours = time // (60 * 60)
    minutes = time // 60 % 60
    seconds = round(time % 60, 2)

    if seconds == 60:
        seconds = 0
        minutes += 1
    if minutes == 60:
        minutes = 0
        hours += 1

    duration = "PT"

    if hours:
        duration += "%dH" % hours
    if minutes:
        duration += "%dM" % minutes
    if seconds > 0:
        seconds = strip_zeros("%.2f" % seconds)
        duration += "%sS" % seconds
    if duration == "PT":
        duration = "PT0S"

    return duration


def strip_zeros(float_str):
    """Recursively strip trailing zeros from a float.

    Zeros in integer part are not affected. If no decimal part is left, the
    decimal separator is also stripped. Underscores as described in PEP 515
    are allowed in the given string and stripped where the trailing digits are
    stripped, but otherwise unaffected.

    >>> strip_zeros("44.10")
    "44.1"
    >>> strip_zeros("44.0")
    "44"
    >>> strip_zeros("1_234_000.000_000")
    "1_234_000"

    :float_str: Float number as string
    :returns: Stripped float as string
    """

    # if '.' is found in the string and string
    # ends in '0', '.' or '_' strip last character
    if float_str.find(".") != -1 and float_str[-1] in ["0", ".", "_"]:
        return strip_zeros(float_str[:-1])

    return float_str


def combine_metadata(stream, indexed_metadata, lose=None, important=None):
    """
    Merge metadata dict to stream metadata dict.

    :param stream: Metadata dict where the new metadata is merged.
    :param metadata: Indexed metadata dict to be merged with.
    :param lose: These are generic values that are allowed to be lost
    :param important: Important values as dict, which will be used
                in conflict situation, if given.
    :returns: Merged metadata dict.
    :raises: ValueError if two different values collide.
    """
    if not indexed_metadata:
        return stream.copy()

    stream = {} if stream is None else stream.copy()
    important = {} if important is None else important
    lose = [] if lose is None else lose

    for stream_index, metadata_dict in six.iteritems(indexed_metadata):

        if stream_index not in stream.keys():
            stream[stream_index] = metadata_dict
            continue

        incomplete_stream = stream[stream_index]

        for key in incomplete_stream.keys():
            if key not in metadata_dict or metadata_dict[key] is None:
                continue

            if incomplete_stream[key] in lose:
                incomplete_stream[key] = metadata_dict[key]
            elif key in important and important[key] not in lose:
                incomplete_stream[key] = important[key]
            elif metadata_dict[key] not in [incomplete_stream[key]] + lose:
                raise ValueError(
                    "Conflict with existing value '%s' and new "
                    "value '%s'." % (incomplete_stream[key],
                                     metadata_dict[key]))

        for key, value in six.iteritems(metadata_dict):
            if key not in incomplete_stream:
                incomplete_stream[key] = value

    return stream


def ensure_text(s, encoding="utf-8", errors="strict"):
    """Coerce *s* to six.text_type.

    For Python 2:
      - `unicode` -> `unicode`
      - `str` -> `unicode`

    For Python 3:
      - `str` -> `str`
      - `bytes` -> decoded to `str`

    Direct copy from release 1.12::
        https://github.com/benjaminp/six/blob/master/six.py#L892

    :encoding: Used encoding
    :errors: Error handling level
    """
    # pylint: disable=invalid-name
    if isinstance(s, six.binary_type):
        return s.decode(encoding, errors)
    elif isinstance(s, six.text_type):
        return s
    else:
        raise TypeError("not expecting type '{}'".format(type(s)))


def _merge_to_stream(stream, method, lose, importants):
    """
    Merges the results of the method into the stream dict.

    Adds item 'method.__name__: method()' into the stream dict.

    If the stream dict already contains an entry with method.__name__ as the
    key, the given lose and importants are examined:
        - Important values are used unless those are lose values.
        - Values within the lose list are overwritten.
        - If neither entry is important or disposable, a ValueError is raised.

    :stream: A dict representing the metadata of a single stream. E.g.
             {"index": 0, "mimetype": "image/png", "width": "500"}
    :method: A metadata method.
    :lose: A list of values that can be overwritten.
    :importants: A dict of keys and values that must not be overwritten.
    :raises: ValueError if the old entry in the stream and the value returned
             by the given method conflict but neither is disposable.
    """
    method_name = method.__name__
    method_value = method()

    if method_name not in stream:
        stream[method_name] = method_value
        return
    elif method_value in lose:
        return
    if stream[method_name] == method_value:
        return

    if method.is_important:
        stream[method_name] = method_value
    elif method_name in importants:
        return
    elif stream[method_name] in lose:
        stream[method_name] = method_value
    else:
        # Set the value as UNAV and raise ValueError
        existing_value = stream[method_name]
        stream[method_name] = UNAV
        raise ValueError("Conflict with existing value '%s' and new value "
                         "'%s' for '%s'." % (existing_value, method_value,
                                             method_name))


def _fill_importants(scraper_results, lose):
    """
    Find the important metadata values from scraper results.

    :scraper_results: A list of lists containing all metadata methods.
    :lose: List of values which can not be important
    :returns: A dict of important metadata values,
              e.g. {"charset": "UTF-8", ...}
    :raises: ValueError if two different important values collide in a method.
    """
    importants = {}
    for model in chain.from_iterable(scraper_results):
        for method in model.iterate_metadata_methods():
            try:
                method_name = method.__name__
                method_value = method()
                if method.is_important and method_value not in lose:
                    if method_name in importants and \
                            importants[method_name] != method_value:
                        raise ValueError(
                            "Conflict with values '%s' and '%s' for '%s': "
                            "both are marked important." %
                            (importants[method_name],
                             method_value,
                             method_name))
                    importants[method_name] = method_value
            except SkipElementException:
                pass

    return importants


def generate_metadata_dict(scraper_results, lose):
    """
    Generate a metadata dict from the given scraper results.

    The resulting dict contains the metadata of each stream as a dict,
    retrievable by using the index of the stream as a key. The indexing
    starts from zero. In case of conflicting values, the error messages
    are reported back to the scraper.

    :scraper_results: A list containing lists of all metadata methods,
                      methods of a single scraper in a single list. E.g.
                      [[scraper1_stream1, scraper1_stream2],
                       [scraper2_stream1, scraper2_stream2]]
    :lose: A list of values that can be overwritten.
    :returns: A tuple of (a dict containing the metadata of the file,
              metadata of each stream in its own dict. E.g.
              {0: {'mimetype': 'video/mp4', 'index': 1,
                   'frame_rate': '30', ...},
               1: {'mimetype': 'audio/mp4', 'index': 2,
                    'audio_data_encoding': 'AAC', ...}},
              and a list of error messages due to conflicting values)

    """
    # if there are no scraper results, return an empty dict
    if not any(scraper_results):
        return {}
    streams = {}
    importants = _fill_importants(scraper_results, lose)

    conflicts = []

    for model in chain.from_iterable(scraper_results):
        stream_index = model.index()

        if stream_index not in streams:
            streams[stream_index] = {}
        current_stream = streams[stream_index]

        for method in model.iterate_metadata_methods():
            try:
                _merge_to_stream(current_stream, method, lose, importants)
            except SkipElementException:
                # happens when the method is not to be indexed
                continue
            # In case of conflicting values, append the error message
            except ValueError as err:
                conflicts.append(str(err))

    return streams, conflicts


def concat(lines, prefix=""):
    """
    Join given list of strings to single string separated with newlines.

    :lines: List of string to join
    :prefix: Prefix to prepend each line with
    :returns: Joined lines as string
    """
    return "\n".join(["%s%s" % (prefix, line) for line in lines])


def sanitize_bytestring(input_bytes):
    """Sanitize unknown byte string as unicode string.

    Function will take a byte string with unknown charset as input and
    and convert it safely to unicode string, removing any non-printable
    characters.

    - decode as utf8 byte string
    - replace non-utf8 characters
    - remove non-printable characters
    - encode string to utf8 before adding to errors

    :input_bytes: Input as byte string
    :returns: Sanitized string as unicode string
    """
    utf8string = input_bytes.decode("utf8", errors="replace")
    sanitized_string = sanitize_string(utf8string)
    return ensure_text(sanitized_string.encode("utf-8"))


def iter_utf_bytes(file_handle, chunksize, charset):
    """
    Iterate given file with matching the bytes with variable length UTF
    characters. The byte sequence might have incomplete UTF characer in the
    end. This is reserved for the next chunk.

    :file_handle: File handle to read
    :chunksize: Size of the chunk to read
    :charset: Character encoding of the file
    :returns: Sequence from the file
    """
    utf_buffer = b""
    chunksize += 4 - chunksize % 4  # needs to be divisible by 4

    def utf_sequence(chunk, sequence_params, possible_le=False):
        """
        Split the given byte chunk to UTF sequence and remainder. Remainder
        is possible if last character of byte chunk is incomplete.

        :chunk: Chunk to match
        :sequenc_params: Dict of smallest and largest byte value of the first
                         byte (or the second in big endian) of a character
        :possible_le: True, little endian is possible, False otherwise
        :returns: Tuple (x, y) where x is UTF sequence and y is remainder
        """
        if len(chunk) < 4:
            return (chunk, b"")

        for params in sequence_params:

            for index in params["indexes"]:
                try:
                    sequence_char = ord(chunk[-index])
                except TypeError:
                    sequence_char = chunk[-index]
                if len(chunk) >= index and \
                        sequence_char >= params["smallest"] and \
                        sequence_char <= params["largest"]:
                    if possible_le and index == 1:
                        index = index + 1  # Move index left for little endian
                    return chunk[:-index], chunk[-index:]

        return (chunk, b"")

    while True:
        chunk = utf_buffer + file_handle.read(chunksize)

        if not chunk:
            return

        if charset.upper() == "UTF-8":
            chunk, utf_buffer = utf_sequence(chunk, [
                {"smallest": 0xc0, "largest": 0xdf, "indexes": [1]},
                {"smallest": 0xe0, "largest": 0xef, "indexes": [1, 2]},
                {"smallest": 0xf0, "largest": 0xf7, "indexes": [1, 2, 3]}])
        elif charset.upper() == "UTF-16":
            chunk, utf_buffer = utf_sequence(
                chunk, [{"smallest": 0xd8, "largest": 0xdb,
                         "indexes": [1, 2]}], True)

        yield chunk
