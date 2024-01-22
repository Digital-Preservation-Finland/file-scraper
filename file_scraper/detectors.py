"""File format detectors."""
# pylint: disable=ungrouped-imports

import distutils.spawn
import os
import zipfile
import lxml.etree as ET
import exiftool

from fido.fido import Fido, defaults
from fido.pronomutils import get_local_pronom_versions
from file_scraper.base import BaseDetector
from file_scraper.shell import Shell
from file_scraper.config import get_value
from file_scraper.defaults import (MIMETYPE_DICT, PRIORITY_PRONOM, PRONOM_DICT,
                                   VERSION_DICT, UNKN)
from file_scraper.utils import encode_path, decode_path
from file_scraper.magiclib import magiclib, magic_analyze
from file_scraper.verapdf.verapdf_scraper import filter_errors, OK_CODES

MAGIC_LIB = magiclib()


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

    def load_fido_xml(self, file):
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

    def setup_format_cache(self):
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

    def __init__(self, filename):
        """
        Initialize the reader.

        Fido is done with old-style python and does not inherit object,
        so super() is not available.

        :filename: File path
        """
        self.filename = filename  # File path
        self.puid = None  # Identified pronom code
        self.mimetype = None  # Identified mime type
        self.version = None  # Identified file format version
        _FidoCachedFormats.__init__(self, quiet=True, format_files=[
            "formats-v95.xml", "format_extensions.xml"])
        self.setup_format_cache()

    def identify(self):
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
            # Python's zipfile module used internally by FIDO doesn't support
            # paths that are provided as byte strings
            filename=decode_path(self.filename), extension=False
        )

    def print_matches(self, fullname, matches, delta_t, matchtype=""):
        """
        Get puid, mimetype and version.

        :fullname: File path
        :matches: Matches tuples in Fido
        :delta_t: Not needed here, but originates from Fido
        :matchtype: Not needed here, but originates from Fido
        """
        # pylint: disable=unused-argument
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

    def _find_mime(self, item):
        """
        Find mimetype and version in Fido.

        :item: Fido result
        """
        mime = item.find("mime")
        self.mimetype = mime.text if mime is not None else None
        version = item.find("version")
        self.version = version.text if version is not None else None
        if self.mimetype in MIMETYPE_DICT:
            self.mimetype = MIMETYPE_DICT[self.mimetype]
        if self.mimetype in VERSION_DICT:
            if self.version in VERSION_DICT[self.mimetype]:
                self.version = \
                    VERSION_DICT[self.mimetype][self.version]


class FidoDetector(BaseDetector):
    """Fido detector."""

    def __init__(self, filename, mimetype=None, version=None):
        """
        Initialize detector.

        :filename: File name of file to detect
        :mimetype: Mimetype from another source, e.g. METS
        :version: File format version from another source, e.g. METS
        """
        super().__init__(filename, mimetype=mimetype,
                         version=version)
        self._puid = None

    def detect(self):
        """Detect file format and version."""
        fido = _FidoReader(self.filename)
        fido.identify()
        self.mimetype = fido.mimetype
        self.version = fido.version
        self._puid = fido.puid
        self.info = {"class": self.__class__.__name__,
                     "messages": [],
                     "errors": [],
                     "tools": []}

    def get_important(self):
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
        important = {}
        if not self._given_mimetype:
            if self._puid in ["fmt/471", "fmt/100"]:
                important["mimetype"] = self.mimetype
            elif self.mimetype not in [None, "text/html", "application/zip"]:
                important["mimetype"] = self.mimetype
        return important


class MagicDetector(BaseDetector):
    """File magic detector."""

    def detect(self):
        """Detect mimetype."""
        mimetype = magic_analyze(MAGIC_LIB, MAGIC_LIB.MAGIC_MIME_TYPE,
                                 self.filename)
        if mimetype in MIMETYPE_DICT:
            self.mimetype = MIMETYPE_DICT[mimetype]
        else:
            self.mimetype = str(mimetype)
        if mimetype == "application/json":
            self.mimetype = "text/plain"

        # DV detection with unpatched file library
        mime_check = mimetype == "application/octet-stream"
        file_extension_check = decode_path(self.filename).endswith(".dv")
        if mime_check and file_extension_check:
            analyze = magic_analyze(
                MAGIC_LIB,
                MAGIC_LIB.MAGIC_NONE,
                self.filename
            )
            if analyze == "DIF (DV) movie file (PAL)":
                self.mimetype = "video/dv"

        self.info = {"class": self.__class__.__name__,
                     "messages": [],
                     "errors": [],
                     "tools": []}

    def get_important(self):
        """
        Important mime types.

        If user has not given a MIME type, we will prefer file detector with
        the following mimetypes:
            - application/vnd.oasis.opendocument.formula

        :returns: A dict possibly containing key "mimetype"
        """
        important = {}
        if (not self._given_mimetype and self.mimetype in
                ["application/vnd.oasis.opendocument.formula"]):
            important["mimetype"] = self.mimetype
        return important


class PredefinedDetector(BaseDetector):
    """A detector for handling user-supplied MIME types and versions."""

    def detect(self):
        """
        No actual detection needed, just use the given values and log messages.

        If the user supplied a MIME type and/or version, it has already been
        recorded during initialization. Giving only the version is not
        possible: if the initilizer is not given a MIME type, the possible
        version information is ignored.
        """
        self.mimetype = self._given_mimetype
        if self._given_mimetype:
            self.version = self._given_version

        if self._given_mimetype:
            messages = ["User-supplied file format used"]
        else:
            messages = []
        self.info = {"class": self.__class__.__name__,
                     "messages": messages,
                     "errors": [],
                     "tools": []}

    def get_important(self):
        """
        The results from this detector are always important.

        If the scraper does not know MIME type or version, the values will be
        None and thus ignored by the scraper.
        """
        return {"mimetype": self.mimetype, "version": self.version}


class VerapdfDetector(BaseDetector):
    """
    Detector for finding the version of PDF/A files.
    """

    def detect(self):
        """
        Run veraPDF to find out if the file is PDF/A and possibly its version.

        If the file is not a PDF/A, the MIME type and version are left as None.
        """
        verapdf_loc = get_value("VERAPDF_PATH")
        if distutils.spawn.find_executable("verapdf") is not None:
            verapdf_loc = "verapdf"
        # --nonpdfext flag allows also files without the .pdf extension
        # --loglevel 1 leaves warnings out of the output, warnings are not
        # useful for detection
        cmd = [verapdf_loc, encode_path(self.filename), "--nonpdfext",
               "--loglevel", "1"]
        shell = Shell(cmd)

        # Test if the file is a PDF/A. If --nonpdfext flag is not supported,
        # it does not affect to the return code.
        if shell.returncode != 0:
            self._set_info_not_pdf_a(shell)
            return
        try:
            report = ET.fromstring(shell.stdout_raw)
            if report.xpath("//batchSummary")[0].get("failedToParse") == "0":
                compliant = report.xpath(
                    "//validationReport")[0].get("isCompliant")
                if compliant == "false":
                    self._set_info_not_pdf_a()
                    return
                profile = \
                    report.xpath("//validationReport")[0].get("profileName")
            else:
                self._set_info_not_pdf_a(shell)
                return
        except ET.XMLSyntaxError:
            self._set_info_not_pdf_a(shell)
            return

        # If we have not encountered problems, the file is PDF/A and its
        # version can be read from the profile.
        version = profile.split("PDF/A")[1].split(" validation profile")[0]
        self.version = f"A{version.lower()}"
        self.mimetype = "application/pdf"
        self.info = {"class": self.__class__.__name__,
                     "messages": ["PDF/A version detected by veraPDF."],
                     "errors": [],
                     "tools": []}

    def _set_info_not_pdf_a(self, error_shell=None):
        """
        Set info to reflect the fact that the file was not a PDF/A
        and thus PDF/A validation isn't performed.

        :error_shell: If a Shell instance is given, its stderr is
                      set as 'errors' in the info if it is not empty.
        """
        self.info = {"class": self.__class__.__name__,
                     "messages": ["INFO: File is not PDF/A, "
                                  "so PDF/A validation is not performed"],
                     "errors": [],
                     "tools": []}

        errors = error_shell.stderr
        if error_shell.returncode in OK_CODES:
            errors = filter_errors(error_shell.stderr)
        if errors:
            self.info["errors"] = [errors]

    def get_important(self):
        """
        If and only if this detector determined a file type, it is important.

        This is to make sure that the PDF/A detection result overrides the
        non-archival result obtained by other detectors.
        """
        if self.mimetype and self.version:
            return {"mimetype": self.mimetype, "version": self.version}
        return {}


class MagicCharset(BaseDetector):
    """Charset detector."""

    _supported = ["text/plain",
                  "text/csv",
                  "text/html",
                  "text/xml",
                  "application/xhtml+xml"]

    def __init__(self, filename, mimetype=None, version=None):
        """Initialize detector."""
        self.charset = None
        super().__init__(filename, mimetype=mimetype,
                         version=version)

    @classmethod
    def is_supported(cls, mimetype):
        """
        Check wheter the detector is supported with given mimetype.

        :mimetype: Mimetype to check
        :returns: True if mimetype is supported, False otherwise
        """
        return mimetype in cls._supported

    def detect(self):
        """Detect charset with MagicLib. A charset is detected from up to
        1 megabytes of data from the beginning of file."""
        messages = []
        errors = []
        charset = magic_analyze(MAGIC_LIB,
                                MAGIC_LIB.MAGIC_MIME_ENCODING,
                                self.filename)

        if charset is None or charset.upper() == "BINARY":
            errors.append("Unable to detect character encoding.")
        elif charset.upper() == "US-ASCII":
            self.charset = "UTF-8"
        elif charset.upper() == "ISO-8859-1":
            self.charset = "ISO-8859-15"
        elif charset.upper() == "UTF-16LE" or \
                charset.upper() == "UTF-16BE":
            self.charset = "UTF-16"
        else:
            self.charset = charset.upper()
        if not errors:
            messages.append(
                "Character encoding detected as %s" % self.charset)

        self.info = {"class": self.__class__.__name__,
                     "messages": messages,
                     "errors": errors,
                     "tools": []}


class ExifToolDetector(BaseDetector):
    """
    Detector used with tiff files. Will tell dng files apart from ordinary tiff
    files.
    """

    def detect(self):
        """
        Run ExifToolDetector to find out the mimetype of a file
        """
        try:
            with exiftool.ExifTool() as et:
                metadata = et.get_metadata(self.filename)
                self.mimetype = metadata.get("File:MIMEType", None)
        except AttributeError:
            with exiftool.ExifToolHelper() as et:
                metadata = et.get_metadata(self.filename)
                self.mimetype = metadata[0].get("File:MIMEType", None)
        self.info = {"class": self.__class__.__name__,
                     "messages": [],
                     "errors": [],
                     "tools": []}

    def get_important(self):
        """
        If ExifTool detector determines the mimetype as dng, it is marked as
        important. This is to make sure that this result overrides other
        detectors, which would detect dng files as tiff files.
        """
        important = {}
        if (not self._given_mimetype and self.mimetype in
                ["image/x-adobe-dng"]):
            important["mimetype"] = self.mimetype
        return important


class SegYDetector(BaseDetector):
    """
    Detector used with SEG-Y files. Identifies SEG-Y files and, if possible,
    their file format version.
    """
    def _analyze_version(self, content):
        """
        Analyze if the content is SEG-Y textual header.
        We use UNKN instead of UNAV, because the value is known to be unknown.
        UNAV is used for missing (incomplete) value.
        :returns: "1.0", "2.0" or "(:unkn)" as file format version, and
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
        if content[3120:3143] == "C40 END TEXTUAL HEADER " or \
                content[3120:3135] == "C40 END EBCDIC ":
            for index in range(0, 40):
                if content[index*80:index*80+4] not in [
                        "C%2d " % (index + 1), "C%-2d " % (index + 1)]:
                    return None

            return UNKN

        return None

    def detect(self):
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
            else:
                raise ValueError
        except (UnicodeDecodeError, IndexError, ValueError):
            self.info = {"class": self.__class__.__name__,
                         "messages": [],
                         "errors": [],
                         "tools": []}
            return

        version = self._analyze_version(content)
        if version is not None:
            self.mimetype = "application/x.fi-dpres.segy"
            self.version = version

        messages = []
        if version == UNKN:
            messages.append("SEG-Y signature is missing, but file most"
                            "likely is a SEG-Y file. File format version can "
                            "not be detected.")

        self.info = {"class": self.__class__.__name__,
                     "messages": messages,
                     "errors": [],
                     "tools": []}

    def get_important(self):
        """
        If SegYDetector determines the mimetype as SEG-Y, the mimetype
        and version are marked as important. This is to make sure that
        this result overrides other detectors, which would detect SEG-Y
        files as plain text files.
        """
        important = {}
        if (not self._given_mimetype and self.mimetype in
                ["application/x.fi-dpres.segy"]):
            important["mimetype"] = self.mimetype
        if (not self._given_version and self.mimetype in
                ["application/x.fi-dpres.segy"]):
            important["version"] = self.version
        return important


class SiardDetector(BaseDetector):
    """
    Detector used with SIARD files. Will identify SIARD files and their
    file format version.
    """

    def detect(self):
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
        # The zipfile module prefers filepaths as strings
        filename = decode_path(self.filename)
        if all((os.path.splitext(filename)[1] == ".siard",
                zipfile.is_zipfile(filename))):
            with zipfile.ZipFile(filename) as zipf:
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

        self.info = {"class": self.__class__.__name__,
                     "messages": [],
                     "errors": [],
                     "tools": []}

    def get_important(self):
        """
        If SiardDetector determines the mimetype as SIARD, the mimetype
        and version are marked as important. This is to make sure that
        this result overrides other detectors, which would detect SIARD
        files as ZIP archive files.
        """
        important = {}
        if (not self._given_mimetype and self.mimetype in
                ["application/x-siard"]):
            important["mimetype"] = self.mimetype
        if (not self._given_version and self.mimetype in
                ["application/x-siard"]):
            important["version"] = self.version
        return important
