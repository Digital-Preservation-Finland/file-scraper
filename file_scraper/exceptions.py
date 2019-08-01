"""Custom scraper-related exceptions."""


class SkipElementException(Exception):
    """Exception to tell the iterator to skip the element.
    We are not able to use None or '' since those are reserved for
    other purposes already.
    """


class ImportantMetadataAlreadyDefined(Exception):
    """Exception to tell that the given key has already been defined as
    important."""
