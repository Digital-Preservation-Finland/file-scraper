"""Utilities for scrapers."""

import hashlib
import re
import string
import unicodedata
import zipfile
from itertools import chain
from pathlib import Path

from file_scraper.defaults import UNAV
from file_scraper.exceptions import SkipElementException
from file_scraper.logger import LOGGER


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
            if isinstance(extra_hash, str):
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


def normalize_charset(charset):
    """
    Normalize charset to its most common and supported form.

    For example, 'US-ASCII' is converted to 'UTF-8' as it is backwards
    compatible and 'UTF-8' is more commonly recognized than 'US-ASCII'.
    :param charset: Charset
    :returns: Normalized charset in upper-case
    """
    if charset is None or charset.upper() == "BINARY":
        return UNAV
    if charset.upper() == "US-ASCII":
        return "UTF-8"
    if charset.upper() == "ISO-8859-1":
        return "ISO-8859-15"
    if charset.upper() == "UTF-16LE" \
            or charset.upper() == "UTF-16BE":
        return "UTF-16"

    return charset.upper()


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
    hours = int(time // (60 * 60))
    minutes = int(time // 60 % 60)
    seconds = round(time % 60, 2)

    if seconds == 60:
        seconds = 0
        minutes += 1
    if minutes == 60:
        minutes = 0
        hours += 1

    duration = "PT"

    if hours:
        duration += f"{hours:d}H"
    if minutes:
        duration += f"{minutes:d}M"
    if seconds > 0:
        seconds = strip_zeros(f"{seconds:.2f}")
        duration += f"{seconds}S"
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


def ensure_text(string, encoding="utf-8", errors="strict"):
    """Coerce string to str.
    """
    # pylint: disable=invalid-name
    if isinstance(string, bytes):
        return string.decode(encoding, errors)
    if isinstance(string, str):
        return string

    raise TypeError(f"not expecting type '{type(string)}'")


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
        stream[method_name] = UNAV
        raise ValueError(
            f"Conflict with values '{existing_value}' and '{method_value}' "
            f"for '{method_name}'.")


def _fill_importants(method, importants, lose):
    """
    Find the important metadata values for a method.

    :method: A metadata method
    :importants: A dictionary of important metadata values
    :lose: List of values which can not be important
    :returns: A dict of important metadata values,
              e.g. {"charset": "UTF-8", ...}
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
              {0: {'mimetype': 'video/h264', 'index': 1,
                   'frame_rate': '30', ...},
               1: {'mimetype': 'audio/aac', 'index': 2,
                    'audio_data_encoding': 'AAC', ...}},
              and a list of error messages due to conflicting values)

    """
    # if there are no scraper results, return an empty dict
    if not any(scraper_results):
        return {}
    streams = {}

    conflicts = []
    importants = {}

    # First iterate methods to fill the importants dictionary with important
    # metadata values from the scraper results
    for model in chain.from_iterable(scraper_results):
        for method in model.iterate_metadata_methods():
            try:
                _fill_importants(method, importants, lose)
            except ValueError as err:
                conflicts.append(str(err))

    # Iterate methods to generate metadata dict
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
        LOGGER.debug(
            "Scraper result %s merged to stream: %s", model, current_stream
        )

    return streams, conflicts


def concat(lines, prefix=""):
    """
    Join given list of strings to single string separated with newlines.

    :lines: List of string to join
    :prefix: Prefix to prepend each line with
    :returns: Joined lines as string
    """
    return "\n".join([f"{prefix}{line}" for line in lines])


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

                if len(chunk) < index:
                    continue

                try:
                    sequence_char = ord(chunk[-index])
                except TypeError:
                    sequence_char = chunk[-index]
                if params["smallest"] <= sequence_char <= params["largest"]:
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


def is_zipfile(filename: Path):
    """
    Check if file is a ZIP file.

    Ideally this would be done using zipfile.is_zipfile function. However there
    is an outstanding issue with that function and thus we can't use it
    directly.

    Relevant Github issue: https://github.com/python/cpython/issues/72680

    :filename: File to check
    """
    if zipfile.is_zipfile(filename):
        try:
            with zipfile.ZipFile(filename):
                return True
        except (OSError, zipfile.BadZipFile):
            return False
    else:
        return False


def filter_unwanted_chars(info_string):
    """Filter out characters that are not compatible with XML 1.1

    Sometimes scraper output contains control characters from the scraping
    tools we use, and we want to get rid of these characters so that scraper
    output is compatible with XML.

    Restricted characters in XML 1.1 are listed here:
    https://www.w3.org/TR/xml11/#charsets

    :info_string: String to run filtering on
    :returns: Filtered string
    """

    unwanted_chars = [(0x00, 0x08), (0x0B, 0x0C), (0x0E, 0x1F),
                      (0x7F, 0x84), (0x86, 0x9F),
                      (0xFDD0, 0xFDDF), (0xFFFE, 0xFFFF),
                      (0x1FFFE, 0x1FFFF), (0x2FFFE, 0x2FFFF),
                      (0x3FFFE, 0x3FFFF), (0x4FFFE, 0x4FFFF),
                      (0x5FFFE, 0x5FFFF), (0x6FFFE, 0x6FFFF),
                      (0x7FFFE, 0x7FFFF), (0x8FFFE, 0x8FFFF),
                      (0x9FFFE, 0x9FFFF), (0xAFFFE, 0xAFFFF),
                      (0xBFFFE, 0xBFFFF), (0xCFFFE, 0xCFFFF),
                      (0xDFFFE, 0xDFFFF), (0xEFFFE, 0xEFFFF),
                      (0xFFFFE, 0xFFFFF), (0x10FFFE, 0x10FFFF)]

    unwanted_ranges = [fr'{chr(low)}-{chr(high)}' for (low, high) in
                       unwanted_chars]
    unwanted_chars_regex_string = '[' + ''.join(unwanted_ranges) + ']'
    unwanted_chars_re_pattern = re.compile(
        unwanted_chars_regex_string)

    return unwanted_chars_re_pattern.sub('', info_string)
