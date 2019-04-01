"""Utilities for scrapers."""
import sys
import os
import unicodedata
import string
import subprocess
import hashlib
import six


def metadata(important=False):
    """Decorator for functions scraping metadata."""
    def _wrap(func):
        func.is_metadata = True
        func.is_important = important
        return func
    return _wrap


def is_metadata(f):
    """Return True if given a function with metadata flag, otherwise False."""
    return callable(f) and getattr(f, 'is_metadata', False)


def encode(filename):
    """Encode Unicode filenames."""
    return ensure_str(filename, encoding=sys.getfilesystemencoding())


def decode(filename):
    """Decode Unicode filenames."""
    return ensure_text(filename, encoding=sys.getfilesystemencoding())


def hexdigest(filename, algorithm='sha1', extra_hash=None):
    """Calculte hash of given file.
    :filename: File path
    :algorithm: Hash algorithm. MD5 or SHA variant.
    :extra_hash: Hash to be appended in calculation
    :returns: Calculated hash
    """
    algorithm = algorithm.replace("-", "").lower().strip()
    checksum = hashlib.new(algorithm)
    with open(filename, 'rb') as input_file:
        for chunk in iter(lambda: input_file.read(1024 * 1024), b''):
            checksum.update(chunk)
        if extra_hash:
            if isinstance(extra_hash, str):
                extra_hash = extra_hash.encode('utf-8')
            checksum.update(extra_hash)
    return checksum.hexdigest()


def sanitize_string(dirty_string):
    """Strip non-printable control characters from unicode string
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
    if duration == 'PT':
        duration = 'PT0S'

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
    if float_str.find(".") != -1 and float_str[-1] in ['0', '.', '_']:
        return strip_zeros(float_str[:-1])

    return float_str


def combine_metadata(stream, indexed_metadata, lose=None, important=None):
    """Merge metadata dict to stream metadata dict.

    Will raise ValueError if two different values collide.

    :param stream: Metadata dict where the new metadata is merged.
    :param metadata: Indexed metadata dict to be merged with.
    :param lose: These are generic values that are allowed to be lost
    :param important: Important values as dict, which will be used
                in conflict situation, if given.
    :returns: Merged metadata dict.
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


def run_command(cmd, stdout=subprocess.PIPE, env=None):
    """Execute command.

    Scraper specific error handling is supported by forwarding exceptions.

    :param cmd: commandline command.
    :param stdout: a file handle can be given, for directing stdout to file.
    :param env: Override process environment variables
    :returns: Tuple (statuscode, stdout, stderr)
    """
    _env = os.environ.copy()

    if env:
        for key, value in six.iteritems(env):
            _env[key] = value

    proc = subprocess.Popen(cmd,
                            stdout=stdout,
                            stderr=subprocess.PIPE,
                            shell=False,
                            env=_env)

    (stdout_result, stderr_result) = proc.communicate()
    if not stdout_result:
        stdout_result = ""
    if not stderr_result:
        stderr_result = ""
    statuscode = proc.returncode
    return statuscode, stdout_result, stderr_result


def metadata(important=False):
    """Decorator to help set a flag attribute to the function that it
    can be collected for metadata.
    :param important: Whether or not this metadata is important and should
        have priority when duplicate metadata key is discovered.
    """

    def _wrapper(func):
        if callable(func):
            func.important = important
            func.metadata = True
        return func

    return _wrapper


def is_metadata(func):
    """To help let scraper know the given function has metadata flagged."""
    return callable(func) and getattr(func, 'metadata', False)


def is_important(func):
    """To help let scraper know the given function is flagged important."""
    return callable(func) and getattr(func, 'important', False)


def ensure_str(s, encoding='utf-8', errors='strict'):
    """Coerce *s* to `str`.

    For Python 2:
      - `unicode` -> encoded to `str`
      - `str` -> `str`

    For Python 3:
      - `str` -> `str`
      - `bytes` -> decoded to `str`

    Direct copy from release 1.12::

        https://github.com/benjaminp/six/blob/master/six.py#L872
    """
    if not isinstance(s, (six.text_type, six.binary_type)):
        raise TypeError("not expecting type '%s'" % type(s))
    if six.PY2 and isinstance(s, six.text_type):
        s = s.encode(encoding, errors)
    elif six.PY3 and isinstance(s, six.binary_type):
        s = s.decode(encoding, errors)
    return s


def ensure_text(s, encoding='utf-8', errors='strict'):
    """Coerce *s* to six.text_type.

    For Python 2:
      - `unicode` -> `unicode`
      - `str` -> `unicode`

    For Python 3:
      - `str` -> `str`
      - `bytes` -> decoded to `str`

    Direct copy from release 1.12::

        https://github.com/benjaminp/six/blob/master/six.py#L892
    """
    if isinstance(s, six.binary_type):
        return s.decode(encoding, errors)
    elif isinstance(s, six.text_type):
        return s
    else:
        raise TypeError("not expecting type '%s'" % type(s))
