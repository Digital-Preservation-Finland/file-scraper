"""Custom scraper-related exceptions."""


class ForbiddenCharacterError(Exception):
    """
    Exception to tell that forbidden characters were found in a
    given text file.
    """


class ImportantMetadataAlreadyDefined(Exception):
    """
    Exception to tell that the given key has already been defined as
    important.
    """


class SkipElementException(Exception):
    """
    Exception to tell the iterator to skip the element.
    We are not able to use None or '' since those are reserved for
    other purposes already.
    """


class UnknownEncodingError(Exception):
    """
    Exception to tell that the used text encoding is unknown
    or that the decoding of a text was otherwise unsuccessful.
    """


class FileIsNotScrapable(Exception):
    """
    Exception to tell the user of the scraper that the filepath given
    is not scrapable
    """


class DirectoryIsNotScrapable(IsADirectoryError):
    """
    Exception to tell the user that the given filepath leads to a directory
    instead of a file.
    """


class FileNotFoundIsNotScrapable(FileNotFoundError):
    """
    Exception to tell the user that the file couldn't be found and that is
    why the file cannot be scraped.
    """


class InvalidMimetype(ValueError):
    """
    Exception when mimetype is not accepted as a parameter
    """


class InvalidVersionForMimetype(ValueError):
    """
    Exception when the version is not accepted as a parameter
    in the context of the mimetype parameter
    """
