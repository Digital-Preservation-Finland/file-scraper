"""Base module for scrapers."""

from __future__ import annotations

import abc
from collections.abc import Iterator
from pathlib import Path
from typing import Any, Generic, Literal, TypeVar

from file_scraper.defaults import UNAP, UNAV
from file_scraper.state import Mimetype
from file_scraper.utils import (
    MetadataMethod,
    filter_unwanted_chars,
    is_metadata,
    metadata,
)


class BaseApparatus(metaclass=abc.ABCMeta):
    """Base class for extractors and detectors."""

    def __init__(
        self,
        filename: Path,
    ) -> None:
        """Initialize extractor/detector.

        :param filename: Path to the file that is to be scraped
        """
        self.filename = filename
        self._messages: list[str] = []
        self._errors: list[str] = []

    def errors(self) -> list[str]:
        """Return the logged errors in a list.

        :returns: copied list containing the logged errors
        """
        return [
            filter_unwanted_chars(error) for error in self._errors if error
        ]

    def messages(self) -> list[str]:
        """Return logged non-empty messages in a list.

        :returns: list containing the logged messages
        """
        return [
            filter_unwanted_chars(message)
            for message in self._messages
            if message
        ]

    @abc.abstractmethod
    def tools(self) -> dict[str, dict[str, Any]]:
        """Return information about the software used by the extractor or
        detector.

        :returns: Dictionary where each key is the name of the software tool,
            and each value is another dictionary containing details about the
            tool (e.g. version). If no tools are available, an empty
            dictionary is returned instead.
        """

    def info(self) -> dict:
        """Return basic info of detector/extractor.

        The returned dict contains keys "class", "messages", "errors"
        and "tools", where:
            class: Name of the class
            messages: List of info messages
            errors: List of errors
            tools: Dictionary of tools used

        :returns: Info dict
        """
        return {
            "class": self.__class__.__name__,
            "messages": self.messages(),
            "errors": self.errors(),
            "tools": self.tools(),
        }


class BaseMeta():
    """
    All metadata is formalized in common data model.

    BaseMeta class will define common metadata for all file formats, such as:
    filename, mimetype, version, checksum.

    Additional metadata and processing is implemented in subclasses.
    """

    _supported: dict[str, list[str]] = {}
    _allow_versions = False

    @metadata()
    def mimetype(self) -> str:
        """
        BaseMeta does no real scraping. Should be implemented in subclasses.
        Resolve only if unambiguous.

        :returns: "(:unav)"
        """
        return UNAV

    @metadata()
    def version(self) -> str:
        """
        BaseMeta does no real scraping. Should be implemented in subclasses.
        Resolve only if unambiguous.

        :returns: "(:unav)"
        """
        return UNAV

    @metadata()
    def index(self) -> int:
        """
        BaseMeta does no real scraping. Should be implemented in subclasses.

        :returns: 0
        """
        return 0

    @metadata()
    def stream_type(self) -> str:
        """
        BaseMeta does no real scraping. Should be implemented in subclasses.
        Resolve only if unambiguous.

        :returns: "(:unav)"
        """
        return UNAV

    @classmethod
    def is_supported(
        cls,
        mimetype: str | None,
        version: str | None = None,
        params: dict | None = None,  # pylint: disable=unused-argument
    ) -> bool:
        """
        Report whether this model supports the given MIME type and version.

        Version None is considered to be a supported version.

        :param mimetype: MIME type to be checked
        :param version: Version to be checked, defaults to None
        :param params: Parameter dict that can be used by some metadata models.
        :returns: True if MIME type is supported and all versions are allowed
            or the version is supported too.
        """
        if mimetype not in cls._supported:
            return False
        return (
            version in cls._supported[mimetype] + [None] or cls._allow_versions
        )

    def iterate_metadata_methods(self) -> Iterator[MetadataMethod]:
        """Iterate through all metadata methods."""
        for method in dir(self):
            if is_metadata(getattr(self, method)):
                yield getattr(self, method)

    @classmethod
    def supported_mimetypes(cls) -> dict[str, list[str]]:
        """Return the dict containing supported mimetypes and versions."""
        return cls._supported


AnyMeta = TypeVar("AnyMeta", bound=BaseMeta)


class BaseExtractor(BaseApparatus, Generic[AnyMeta]):
    """Base extractor implements common methods for all extractors."""

    _supported_metadata: list[type[AnyMeta]] = []
    _only_wellformed = False

    def __init__(
        self,
        filename: Path,
        mimetype: str | None,
        version: str | None = None,
        params: dict | None = None,
    ) -> None:
        """
        Initialize extractor.

        BaseExtractor.stream will contain all streams in standardized metadata
        data model.

        :param filename: Path to the file that is to be scraped
        :param mimetype: Predefined mimetype
        :param version: Predefined file format version
        :param params: Extra parameters that some extractors can use.
        """
        super().__init__(filename)

        self._predefined_mimetype = mimetype
        self._predefined_version = version
        self.streams: list[AnyMeta] = []
        self._params = params if params is not None else {}

    @property
    def well_formed(self) -> bool | None:
        """
        Return well-formedness status of the scraped file.

        :returns: None if extractor does not check well-formedness, True if the
            file has been scraped without errors and otherwise False
        """
        return len(self._messages) > 0 and len(self._errors) == 0

    @classmethod
    def is_supported(
        cls,
        mimetype: str | None,
        version: str | None = None,
        check_wellformed: bool = True,
        params: dict | None = None,  # pylint: disable=unused-argument
    ) -> bool:
        """
        Report whether the extractor supports the given MIME type and version.

        The extractor is considered to support the MIME type and version
        combination if at least one of the metadata models supported by the
        extractor supports the combination. If the extractor can only be
        used to check the well-formedness of the file and well-formedness
        check is not wanted, False is returned.

        :param mimetype: MIME type of a file
        :param version: Version of a file. Defaults to None.
        :param check_wellformed: True for scraping with well-formedness check,
            False for skipping the check. Defaults to True.
        :param params: dict of other parameters that can be used by overriding
            methods
        :returns: True if the MIME type and version are supported, False if not
        """
        if cls._only_wellformed and not check_wellformed:
            return False
        return any(
            x.is_supported(mimetype, version) for x in cls._supported_metadata
        )

    def _check_supported(
        self,
        allow_unav_mime: bool = False,
        allow_unav_version: bool = False,
        allow_unap_version: bool = False,
    ) -> None:
        """
        Check that the determined MIME type and version are supported.

        :param allow_unav_mime: True if (:unav) is an acceptable MIME type
        :param allow_unav_version: True if (:unav) is an acceptable version
        :param allow_unap_version: True if (:unap) is an acceptable version
        """
        # If there are no streams, the extractor does not support the
        # determined MIME type and version combination at all (i.e. the
        # initial MIME type guess used to choose extractors has been
        # inaccurate).
        if not self.streams:
            self._errors.append("MIME type not supported by this extractor.")
            return

        mimetype = self.streams[0].mimetype()
        version = self.streams[0].version()

        if mimetype is None:
            self._errors.append("None is not a supported MIME type.")

        if mimetype == UNAV and allow_unav_mime:
            return

        for md_class in self._supported_metadata:
            supported = md_class.supported_mimetypes().get(mimetype, None)
            if supported is None:
                continue
            # version is in the list of supported versions
            # or all versions are supported (empty list)
            if version in supported or not supported:
                return
            # version is (:unav) or (:unap) but that is allowed
            if (allow_unav_version and version == UNAV) or (
                allow_unap_version and version == UNAP
            ):
                return

        # No supporting metadata models found.
        self._errors.append(
            f"MIME type {mimetype} with version {version} is not supported."
        )

    def iterate_models(self, **kwargs: Any) -> Iterator[AnyMeta]:
        """
        Iterate Extractor models.

        :param kwargs: Model specific parameters
        :returns: Metadata model
        """
        for md_class in self._supported_metadata:
            if md_class.is_supported(
                self._predefined_mimetype,
                self._predefined_version,
                self._params,
            ):
                yield md_class(**kwargs)

    @abc.abstractmethod
    def extract(self):
        """Implemented in subclasses."""


class BaseDetector(BaseApparatus):
    """
    Class to identify the mimetype and version of the file.
    """

    def __init__(
        self,
        filename: Path,
    ) -> None:
        """Initialize detector.

        :param filename: Path to the identified file
        """
        super().__init__(filename)

        self._mimetype = None  # Identified mimetype
        self.version = None  # Identified file version

    @property
    def well_formed(self) -> Literal[False] | None:
        """Return well-formedness status of the detected file.

        This can be either None or False, because detectors do not validate.

        :returns: False if errors in detection, None otherwise.
        """
        return False if self._errors else None

    @abc.abstractmethod
    def detect(self) -> None:
        """Detect file. Must be implemented in detectors."""

    def determine_important(self) -> Mimetype | None:
        """
        Used to replace existing mimetype with a more important result.
        :returns: an important Mimetype or None.
        """
        return None

    @property
    def mimetype(self) -> str | None:
        """Return mimetype"""
        return self._mimetype

    @mimetype.setter
    def mimetype(self, value: str | None) -> None:
        """Setter for mimetype property"""
        if value is None:
            self._mimetype = None
        else:
            self._mimetype = value.lower()
