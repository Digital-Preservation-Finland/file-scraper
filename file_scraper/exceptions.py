"""Custom scraper-related exceptions."""


class ConflictingValueError(Exception):
    """Exception to tell that merging of important keys resulted in a
    conflict between values.
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
