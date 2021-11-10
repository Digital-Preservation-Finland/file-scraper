"""Custom scraper-related exceptions."""


class ForbiddenCharacterError(Exception):
    """Exception to tell that forbidden characters were found in a
    given text file.
    """


class ImportantMetadataAlreadyDefined(Exception):
    """Exception to tell that the given key has already been defined as
    important.
    """


class SkipElementException(Exception):
    """Exception to tell the iterator to skip the element.
    We are not able to use None or '' since those are reserved for
    other purposes already.
    """


class UnknownEncodingError(Exception):
    """Exception to tell that the used text encoding is unknown
    or that the decoding of a text was otherwise unsuccessful.
    """
