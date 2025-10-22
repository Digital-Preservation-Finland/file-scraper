"""File format detectors."""
from __future__ import annotations

import errno
import gzip
import os
import zipfile
from pathlib import Path
from typing import Literal

import exiftool
import lxml.etree
from fido import __version__ as fido_version
from fido.fido import Fido, defaults
from fido.pronomutils import get_local_pronom_versions

from file_scraper.base import BaseDetector
from file_scraper.defaults import (
    MIMETYPE_DICT,
    PRIORITY_PRONOM,
    PRONOM_DICT,
    UNAP,
    UNKN,
    VERSION_DICT,
)
from file_scraper.state import Mimetype
from file_scraper.logger import LOGGER
from file_scraper.magiclib import magic_analyze, magiclib, magiclib_version
from file_scraper.utils import is_zipfile, normalize_charset


class _FidoCachedFormats(Fido):
    """Class whose sole purpose is to override one of the default function
    provided by Fido by caching the fido XML data.

    This is made to optimize the usage of Fido via the use of
    cache-pattern. Fido has an issue that for one file at a time, it needs
    to read format XML file. This will cause slowness when detecting batches
    of files, because Fido needs to re-read the same XML and assign values
    to specific attributes. Thus this class strives to minimize the need to
    re-read the same format XML.
    """

    _use_cached = False
    _cached_formats = None
    _cached_puid_format_map = None
    _cached_puid_has_priority_over_map = None

    def load_fido_xml(
        self, file: str | os.PathLike
    ) -> list[lxml.etree._Element]:
        """Overloads the default load_fido_xml so that it has an option to
        prevent being called again.

        If data has been cached, will use that data instead.

        :param file: File that will be loaded.
        """
        if _FidoCachedFormats._use_cached:
            self.formats = _FidoCachedFormats._cached_formats
            self.puid_format_map = _FidoCachedFormats._cached_puid_format_map
            self.puid_has_priority_over_map = \
                _FidoCachedFormats._cached_puid_has_priority_over_map
        else:
            Fido.load_fido_xml(self, file=file)

        return self.formats

    def setup_format_cache(self) -> None:
        """Function to explicitly cache the current formats. If cache has
        already been set, this function will not do anything."""
        if not _FidoCachedFormats._use_cached:
            _FidoCachedFormats._cached_formats = self.formats
            _FidoCachedFormats._cached_puid_format_map = self.puid_format_map
            _FidoCachedFormats._cached_puid_has_priority_over_map = \
                self.puid_has_priority_over_map
            _FidoCachedFormats._use_cached = True


class _FidoReader(_FidoCachedFormats):
    """Fido wrapper to get pronom code, mimetype and version."""

    def __init__(self, filename: str | os.PathLike) -> None:
        """
        Initialize the reader.

        Fido is done with old-style python and does not inherit object,
        so super() is not available.

        :param filename: File path
        """
        self.filename = filename  # File path
        self.puid = None  # Identified pronom code
        self.mimetype = None  # Identified mime type
        self.version = None  # Identified file format version
        _FidoCachedFormats.__init__(self, quiet=True, format_files=[
            "formats-v95.xml", "format_extensions.xml"])
        self.setup_format_cache()

    def identify(self) -> None:
        """Identify file format with using pronom registry."""
        versions = get_local_pronom_versions()
        defaults["xml_pronomSignature"] = versions.pronom_signature
        defaults["containersignature_file"] = \
            versions.pronom_container_signature
        defaults["xml_fidoExtensionSignature"] = \
            versions.fido_extension_signature
        defaults["format_files"] = [defaults["xml_pronomSignature"]]
        defaults["format_files"].append(
            defaults["xml_fidoExtensionSignature"])
        self.identify_file(
            # FIDO does not work well with pathlib paths
            filename=str(self.filename), extension=False
        )

    def print_matches(
        self,
        fullname: str,
        matches: list[tuple[lxml.etree._Element, str]],
        delta_t: float,
        matchtype: str = "",
    ) -> None:
        """
        Get puid, mimetype and version.

        :param fullname: File path
        :param matches: Matches tuples in Fido
        :param delta_t: Not needed here, but originates from Fido
        :param matchtype: Not needed here, but originates from Fido
        """
        for (item, _) in matches:
            self.puid = self.get_puid(item)
            if self.puid in PRONOM_DICT:
                (self.mimetype, self.version) = PRONOM_DICT[self.puid]
                return

        for (item, _) in matches:
            self.puid = self.get_puid(item)
            if self.puid in PRIORITY_PRONOM:
                self._find_mime(item)
                return

        for (item, _) in matches:
            if self.mimetype is None:
                self.puid = self.get_puid(item)
                self._find_mime(item)

    def _find_mime(self, item: lxml.etree._Element) -> None:
        """
        Find mimetype and version in Fido.

        :param item: Fido result
        """
        mime = item.find("mime")
        self.mimetype = mime.text if mime is not None else None
        version = item.find("version")
        self.version = version.text if version is not None else None
        if self.mimetype in MIMETYPE_DICT:
            self.mimetype = MIMETYPE_DICT[self.mimetype]
        if (
            self.mimetype in VERSION_DICT
            and self.version in VERSION_DICT[self.mimetype]
        ):
            self.version = VERSION_DICT[self.mimetype][self.version]


class FidoDetector(BaseDetector):
    """Fido detector."""

    def __init__(
        self,
        filename: Path,
    ) -> None:
        """
        Initialize detector.

        :param filename: File name of file to detect
        """
        super().__init__(filename)
        self._puid = None

    def detect(self) -> None:
        """Detect file format and version."""
        fido = _FidoReader(self.filename)
        fido.identify()
        self.mimetype = fido.mimetype
        self.version = fido.version
        self._puid = fido.puid

        # FIDO does not detect version for WARCs
        if self.version is None and self.mimetype in {
            "application/gzip",
            "application/warc",
        }:
            self.version = self.read_warc_version(
                self.filename, self.mimetype == "application/gzip"
            )
            if self.version is not None:
                self.mimetype = "application/warc"

    def determine_important(self) -> Mimetype | None:
        """
        Return important mime types.

        We will always prefer Fido except in the the following cases:
            - text/html when it is not HTML5 or HTML4.01.
              HTML variant is recognized with pronom code.
            - application/zip
            - user has given a MIME type

        Fido recognizes ARC files as text/html and OpenOffice Formula files
        as application/zip, therefore these are given to other detectors.

        :returns: A dict possibly containing key "mimetype"
        """

        arc_or_formula = self._puid in ["fmt/471", "fmt/100"]
        nonstandard_mimetype = self.mimetype not in {
            None,
            "text/html",
            "application/zip",
        }

        if arc_or_formula or nonstandard_mimetype:
            return Mimetype(self.mimetype, None)

    def tools(self) -> dict:
        """Return information about the software used by the extractor or
        detector.

        :returns: Dictionary where each key is the name of the software tool,
            and each value is another dictionary containing details about the
            tool (e.g. version). If no tools are available, an empty
            dictionary is returned instead.
        """
        return {
            "fido": {"version": fido_version}
        }

    @staticmethod
    def read_warc_version(file_path: str | Path, gz: bool) -> str | None:
        """Read the version of a WARC file.

        :param file_path: Path to WARC file.
        :param gz: Is the WARC gzipped.
        :returns: WARC version or `None` if version could not be read.
        """
        func = gzip.open if gz else open
        with func(file_path, "rt", encoding="utf-8") as file:
            line = file.readline().strip()
            if not line.startswith("WARC/"):
                return None
            return line.split("/")[1]


class MagicDetector(BaseDetector):
    """File magic detector."""

    def detect(self) -> None:
        """Detect mimetype."""
        magic_lib = magiclib()
        mimetype = magic_analyze(magic_lib, magic_lib.MAGIC_MIME_TYPE,
                                 self.filename)
        if mimetype in MIMETYPE_DICT:
            self.mimetype = MIMETYPE_DICT[mimetype]
        else:
            self.mimetype = str(mimetype)
        if mimetype == "application/json":
            self.mimetype = "text/plain"

        # DV detection with unpatched file library
        mime_check = mimetype == "application/octet-stream"
        file_extension_check = self.filename.suffix == ".dv"
        if mime_check and file_extension_check:
            analyze = magic_analyze(
                magic_lib,
                magic_lib.MAGIC_NONE,
                self.filename
            )
            if analyze == "DIF (DV) movie file (PAL)":
                LOGGER.info(
                    "Magic detection overridden to 'video/dv' per manual check"
                )
                self.mimetype = "video/dv"

    def determine_important(self) -> Mimetype | None:
        """
        Important mime types.

        If user has not given a MIME type, we will prefer file detector with
        the following mimetypes:
            - application/vnd.oasis.opendocument.formula

        :returns: A dict possibly containing key "mimetype"
        """
        if self.mimetype in ["application/vnd.oasis.opendocument.formula"]:
            return Mimetype(self.mimetype, None)

    def tools(self) -> dict[str, dict[str, str]]:
        """Return information about the software used by the extractor or
        detector.

        :returns: Dictionary where each key is the name of the software tool,
            and each value is another dictionary containing details about the
            tool (e.g. version). If no tools are available, an empty
            dictionary is returned instead.
        """
        return {"magiclib": {"version": magiclib_version()}}


class MagicCharset(BaseDetector):
    """Charset detector."""

    _supported = ["text/plain",
                  "text/csv",
                  "text/html",
                  "text/xml",
                  "application/xhtml+xml"]

    def __init__(
        self,
        filename: Path,
    ) -> None:
        """Initialize detector."""
        self.charset = None
        super().__init__(filename)

    @classmethod
    def is_supported(cls, mimetype: str | None) -> bool:
        """
        Check wheter the detector is supported with given mimetype.

        :param mimetype: Mimetype to check
        :returns: True if mimetype is supported, False otherwise
        """
        return mimetype in cls._supported

    def detect(self) -> None:
        """Detect charset with MagicLib. A charset is detected from up to
        1 megabytes of data from the beginning of file.
        """
        charset = magic_analyze(magiclib(),
                                magiclib().MAGIC_MIME_ENCODING,
                                self.filename)

        if charset is None or charset.upper() == "BINARY":
            self._errors.append("Unable to detect character encoding.")
        else:
            self.charset = normalize_charset(charset)
        if not self._errors:
            self._messages.append(
                f"Character encoding detected as {self.charset}"
            )

    def tools(self) -> dict[str, dict[str, str]]:
        """Return information about the software used by the extractor or
        detector.

        :returns: Dictionary where each key is the name of the software tool,
            and each value is another dictionary containing details about the
            tool (e.g. version). If no tools are available, an empty
            dictionary is returned instead.
        """
        return {"magiclib": {"version": magiclib_version()}}


class ExifToolDetector(BaseDetector):
    """
    Detector used with tiff and pdf files.

    - tell dng files apart from ordinary tiff files
    - detect PDF/A conformance for PDF files
    - detect PDF/A version
    """

    def detect(self) -> None:
        """
        Run ExifToolDetector to find out the mimetype of a file and to check
        PDF/A conformance for pdf files. PDF/A file version is also detected.

        If the file is pdf file but not a PDF/A, the MIME type and version are
        left as None as the file format identification will be handled by
        other detectors.
        """
        # Try-except is needed because calling et.get_metadata() may raise
        # an ExifToolExecuteError in cases where e.g. the mimetype is defined
        # but the file is not valid and therefore, the metadata can't be
        # fetched by ExifTool.
        try:
            with exiftool.ExifToolHelper() as et:
                metadata = et.get_metadata(self.filename)
                self.mimetype = metadata[0].get("File:MIMEType", None)
                self._detect_pdf_a(metadata[0])
        except exiftool.exceptions.ExifToolExecuteError:
            LOGGER.info("ExifTool could not process file", exc_info=True)
            self._set_info_exiftool_not_supported()

    def _detect_pdf_a(self, metadata: dict) -> None:
        """
        Detect PDF/A and its version from metadata.
        """
        if metadata.get("XMP:Conformance") and metadata.get("XMP:Part"):
            conformance = metadata.get("XMP:Conformance")
            pdf_a_version = metadata.get("XMP:Part")
            self.version = "A-" + str(pdf_a_version) + conformance.lower()
            self._messages.append("PDF/A version detected by Exiftool.")
        elif self.mimetype == "application/pdf":
            self._set_info_not_pdf_a()

    def _set_info_not_pdf_a(self) -> None:
        """
        Set info to reflect the fact that the file was not a PDF/A
        and thus PDF/A validation isn't performed.
        """
        self._messages.append(
            "INFO: File is not PDF/A, so PDF/A validation will not be "
            "performed when validating the file"
        )

    def _set_info_exiftool_not_supported(self) -> None:
        """
        Set info to reflect the fact that the file type is not supported by
        ExifTool, and thus file format detection isn't performed.
        """
        self._messages.append(
            "INFO: The file is not supported by ExifTool, file format "
            "detection could not be performed by this tool"
        )

    def determine_important(self) -> Mimetype | None:
        """
        If ExifTool detector determines the mimetype as dng, it is marked as
        important. This is to make sure that this result overrides other
        detectors, which would detect dng files as tiff files.
        """
        if self.mimetype in ["image/x-adobe-dng"]:
            return Mimetype(self.mimetype, None)
        elif self.mimetype and self.version:
            return Mimetype(self.mimetype, self.version)

    def tools(self) -> dict[str, dict[str, str]]:
        """Return information about the software used by the extractor or
        detector.

        :returns: Dictionary where each key is the name of the software tool,
            and each value is another dictionary containing details about the
            tool (e.g. version). If no tools are available, an empty
            dictionary is returned instead.
        """
        try:
            with exiftool.ExifToolHelper() as et:
                return {"exiftool": {"version": et.version}}
        except exiftool.exceptions.ExifToolExecuteError:
            LOGGER.warning(
                "Could not retrieve ExifTool version", exc_info=True
            )
            return {}


class SegYDetector(BaseDetector):
    """
    Detector used with SEG-Y files. Identifies SEG-Y files and, if possible,
    their file format version.
    """
    def _analyze_version(
        self, content: str
    ) -> Literal["1.0", "2.0", "(:unkn)"] | None:
        """
        Analyze if the content is SEG-Y textual header.
        We use UNKN instead of UNAV, because the value is known to be unknown.
        UNAV is used for missing (incomplete) value.

        :returns: "1.0", "2.0" or "(:unkn)" as file format version or
            None if the file is not SEG-Y file
        """
        if len(content) < 3200:
            return None
        if content[3040:3054] == "C39 SEG Y REV1":
            return "1.0"
        if content[3040:3056] == "C39 SEG-Y REV2.0":
            return "2.0"

        # In case the SEG-Y declaration is missing, we follow the structure.
        # Header contains 40 "cards". Each of them are 80 characters long
        # and begin with a card number "C 1 " ... "C40 ". Here we also allow
        # left-justified card numbering, i.e. "C1  " instead of "C 1 ".
        markers = (
            "C40 END TEXTUAL HEADER ",
            "C40 END EBCDIC ",
            "C40 EOF.",
        )
        if any(
            content[3120:3120 + len(marker)] == marker for marker in markers
        ):
            for index in range(0, 40):
                allowed_markers = [
                    f"C{index + 1:2d} ",  # "C1 "
                    f"C{index + 1:<2d} ",  # "C 1 "
                    f"C{index + 1:02d} ",  # "C01 "
                ]
                if content[index * 80:index * 80 + 4] not in allowed_markers:
                    return None

            return UNKN

        # For some SEG-Y files, the card marker has no number, and is instead
        # just repeated 40 times.
        if content[0] == "C":
            for i in range(1, 40):
                if content[i*80] != "C":
                    return None

            return UNKN

        return None

    def detect(self) -> None:
        """
        Run detection to find MIME type and version.
        """
        with open(self.filename, "rb") as fhandler:
            byte_content = fhandler.read(3200)
        try:
            # The first character has to be "C", with ASCII or EBCDIC encoding
            if byte_content[0] == 0x43:
                content = byte_content.decode('ascii')
            elif byte_content[0] == 0xC3:
                content = byte_content.decode('cp500')  # EBCDIC coding
            elif len(byte_content) == 3200:  # At least 3200 bytes of data
                # Header might be missing and be replaced entirely with
                # whitespace. This is very dubious, but allow this as long
                # as the file extension is correct.
                filename = os.fsencode(self.filename)
                is_file_ext_correct = (
                    filename.lower().endswith(b".sgy")
                    or filename.lower().endswith(b".segy")
                )
                if not is_file_ext_correct:
                    raise ValueError

                is_empty_header = byte_content in (
                    b" " * 3200,  # ASCII encoding
                    b"@" * 3200   # EBCDIC encoding
                )
                if is_empty_header:
                    # If the header is empty, assume SEG-Y file of unknown
                    # version is used. We bail out early, because we can't
                    # analyze a non-existent header.
                    self._messages.append(
                        "SEG-Y header is blank with only whitespace, "
                        "but '.sgy/.segy' file extension is used. "
                        "Assuming SEG-Y file of unknown version."
                    )
                    self.mimetype = "application/x.fi-dpres.segy"
                    self.version = UNKN
                    return
                raise ValueError
            else:
                raise ValueError
        except (IndexError, ValueError):
            return

        version = self._analyze_version(content)
        if version is not None:
            self.mimetype = "application/x.fi-dpres.segy"
            self.version = version

        if version == UNKN:
            self._messages.append(
                "SEG-Y signature is missing, but file most"
                "likely is a SEG-Y file. File format version can "
                "not be detected."
            )

    def determine_important(self) -> Mimetype | None:
        """
        If SegYDetector determines the mimetype as SEG-Y, the mimetype
        and version are marked as important. This is to make sure that
        this result overrides other detectors, which would detect SEG-Y
        files as plain text files.
        """
        if self.mimetype in ["application/x.fi-dpres.segy"]:
            return Mimetype(self.mimetype, self.version)

    def tools(self) -> dict:
        """Return information about the software used by the extractor or
        detector.

        :returns: Dictionary where each key is the name of the software tool,
            and each value is another dictionary containing details about the
            tool (e.g. version). If no tools are available, an empty
            dictionary is returned instead.
        """
        return {}


class AtlasTiDetector(BaseDetector):
    """
    Detector used with ATLAS TI project bundle files.
    Will identify ATLPROJ files and their file format version.
    """

    def detect(self) -> None:
        """
        Run AtlasTiDetector to find out the mimetype and file format
        version of a file. The detector checks::

            1) The file must have a file extension ".atlproj"
            2) The file must be a ZIP archive file

        """
        if self.filename.suffix == ".atlproj" and is_zipfile(self.filename):
            self.mimetype = "application/x.fi-dpres.atlproj"
            self.version = UNAP

    def determine_important(self) -> Mimetype | None:
        """
        If AtlasTiDetector determines the mimetype as x.fi-dpres.atlproj,
        the mimetype and version are marked as important. This is to make
        sure that this result overrides other detectors, which would detect
        atlproj files as ZIP archive files.
        """
        if self.mimetype in ["application/x.fi-dpres.atlproj"]:
            return Mimetype(self.mimetype, self.version)

    def tools(self) -> dict:
        """Return information about the software used by the extractor or
        detector.

        :returns: Dictionary where each key is the name of the software tool,
            and each value is another dictionary containing details about the
            tool (e.g. version). If no tools are available, an empty
            dictionary is returned instead.
        """
        return {}


class SiardDetector(BaseDetector):
    """
    Detector used with SIARD files. Will identify SIARD files and their
    file format version.
    """

    def detect(self) -> None:
        """
        Run SiardDetector to find out the mimetype and file format
        version of a file. The detector checks::

            1) The file must have a file extension ".siard"
            2) The file must be a ZIP archive file
            3) The ZIP archive file must contain a folder
               "header/siardversion/XX"

        The file format version is present in the following path within
        a valid SIARD file: "header/siardversion/<version>/"
        """
        version_folders = []
        if self.filename.suffix == ".siard" and is_zipfile(self.filename):
            with zipfile.ZipFile(self.filename) as zipf:
                version_folders = [
                    x for x in zipf.namelist() if "header/siardversion" in x]

        if version_folders:
            self.mimetype = "application/x-siard"
            for version_folder in version_folders:
                # Get version from header/siardversion path
                if not version_folder.endswith("siardversion/"):
                    version = version_folder.strip("/").split("/")[-1]
                    # Version 2.1 is identical to version 2.1.1
                    if version == "2.1":
                        version = "2.1.1"
                    self.version = version
                    break

    def determine_important(self) -> Mimetype | None:
        """
        If SiardDetector determines the mimetype as SIARD, the mimetype
        and version are marked as important. This is to make sure that
        this result overrides other detectors, which would detect SIARD
        files as ZIP archive files.
        """
        if self.mimetype in ["application/x-siard"]:
            return Mimetype(self.mimetype, self.version)

    def tools(self) -> dict:
        """Return information about the software used by the extractor or
        detector.

        :returns: Dictionary where each key is the name of the software tool,
            and each value is another dictionary containing details about the
            tool (e.g. version). If no tools are available, an empty
            dictionary is returned instead.
        """
        return {}


class ODFDetector(BaseDetector):
    """Detector for OpenDocument Format files.

    All ODF files except ODF formula can be detected by FidoDetector and
    MagicDetector. FidoDetector can not detect ODF formula at all, and
    MagicDetector can not detect the format version. This detector was
    created to add support for ODF formula, but of course if detects the
    mimetype and format version of all other ODF files also.
    """

    def detect(self) -> None:
        """Detect the mimetype and file format version of a file.

        The detector checks that::

            1) The file is a ZIP archive
            2) Valid mimetype is found in "mimetype" file
            3) Valid format version is defined in "meta.xml" file
        """
        # Try to read "mimetype" and "meta.xml" files from zip
        if not is_zipfile(self.filename):
            # The file is not ZIP, so it is not ODF
            return
        with zipfile.ZipFile(self.filename) as zipf:
            if {'mimetype', 'meta.xml'} <= set(zipf.namelist()):
                try:
                    mimetype_file = zipf.read('mimetype')
                    meta_xml_file = zipf.read('meta.xml')
                except OSError as exception:
                    if exception.errno == errno.EINVAL:
                        self._errors.append('Corrupted ZIP archive')
                        return
                    # Unknown error
                    raise
            else:
                # ZIP does not contains required files, so it is not
                # ODF
                return

        # Detect mimetype from "mimetype" file.
        mimetype = mimetype_file.decode().strip()
        if mimetype in (
            'application/vnd.oasis.opendocument.text',
            'application/vnd.oasis.opendocument.spreadsheet',
            'application/vnd.oasis.opendocument.presentation',
            'application/vnd.oasis.opendocument.graphics',
            'application/vnd.oasis.opendocument.formula'
        ):
            detected_mimetype = mimetype
        else:
            # Unknown mimetype
            return

        # Detect format version from "meta.xml" file.
        try:
            tree = lxml.etree.fromstring(meta_xml_file)
        except lxml.etree.XMLSyntaxError:
            self._errors.append('The meta.xml of ODF file is invalid')
            return
        office_ns = tree.nsmap["office"]
        version = tree.attrib[f"{{{office_ns}}}version"]
        if version in ('1.0', '1.1', '1.2', '1.3'):
            detected_version = version
        else:
            # Unknown format version
            LOGGER.info("Unknown format version %s", version)
            return

        # Both variables were detected, so the file most likely is an
        # ODF file
        self.mimetype = detected_mimetype
        self.version = detected_version

    def determine_important(self) -> Mimetype | None:
        """Return dict of important values determined by the detector.

        Mimetype and format version are important because other
        detectors do not detect them correctly.
        """
        return Mimetype(self.mimetype, self.version)

    def tools(self) -> dict[str, dict[str, str]]:
        """Return information about the software used by the extractor or
        detector.

        :returns: Dictionary where each key is the name of the software tool,
            and each value is another dictionary containing details about the
            tool (e.g. version). If no tools are available, an empty
            dictionary is returned instead.
        """
        # Version consists of 4 values. Expect the first 3 to follow SemVers
        major, minor, patch, extra = lxml.etree.LXML_VERSION
        return {
            "lxml": {"version": f"{major}.{minor}.{patch}.{extra}"}
        }


class EpubDetector(BaseDetector):
    """
    Detector used with EPUB files. Will identify EPUB files and their
    file format version.
    """

    def detect(self) -> None:
        """
        Run EpubDetector to find out the mimetype and file format
        version of a file. The detector checks::

            1) The file must be a ZIP archive file
            2) The ZIP archive file must contain a file with the
               extension .opf
            3) The .opf file must be an XML file, whose root element
               contains an attribute "version"
            4) The root element of the .opf file must be
               {http://www.idpf.org/2007/opf}package
            5) The root element must contain a version attribute, whose
               value is the main file format version (i.e. 2.0 or 3.0)

        The file format version is present in the attribute value
        """
        version = None

        if is_zipfile(self.filename):
            with zipfile.ZipFile(self.filename) as zipf:
                for filepath in zipf.namelist():
                    if os.path.splitext(filepath)[1] != ".opf":
                        continue
                    with zipf.open(filepath) as opf:
                        try:
                            root = lxml.etree.parse(opf).getroot()
                            if root.tag == (
                                    '{http://www.idpf.org/2007/opf}package'):
                                version = root.get('version')
                        except lxml.etree.XMLSyntaxError:
                            LOGGER.info(
                                "Ignoring unparseable XML file '%s' in '%s'",
                                filepath, self.filename
                            )

        # Map the valid attribute values to supported versions
        if version == "2.0":
            self.mimetype = "application/epub+zip"
            self.version = "2.0.1"
        elif version == "3.0":
            self.mimetype = "application/epub+zip"
            self.version = "3"

    def determine_important(self) -> Mimetype | None:
        """
        If EpubDetector determines the mimetype as EPUB, the mimetype
        and version are marked as important.
        """
        if self.mimetype in ["application/epub+zip"]:
            return Mimetype(self.mimetype, self.version)

    def tools(self) -> dict[str, dict[str, str]]:
        """Return information about the software used by the extractor or
        detector.

        :returns: Dictionary where each key is the name of the software tool,
            and each value is another dictionary containing details about the
            tool (e.g. version). If no tools are available, an empty
            dictionary is returned instead.
        """
        # Version consists of 4 values. Expect the first 3 to follow SemVers
        major, minor, patch, extra = lxml.etree.LXML_VERSION
        return {
            "lxml": {"version": f"{major}.{minor}.{patch}.{extra}"}
        }
