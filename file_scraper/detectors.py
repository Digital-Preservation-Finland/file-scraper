"""File format detectors."""
# pylint: disable=ungrouped-imports
from __future__ import unicode_literals

import ctypes

import lxml.etree as ET
import six

from fido.fido import Fido, defaults
from fido.pronomutils import get_local_pronom_versions
from file_scraper.base import BaseDetector
from file_scraper.shell import Shell
from file_scraper.config import VERAPDF_PATH
from file_scraper.defaults import (MIMETYPE_DICT, PRIORITY_PRONOM, PRONOM_DICT,
                                   VERSION_DICT)
from file_scraper.utils import encode_path, decode_path

try:
    from file_scraper.config import MAGIC_LIBRARY

    # Monkeypatch magic to load a newer version of the 'magic' shared library
    ctypes.cdll.LoadLibrary(MAGIC_LIBRARY)
except OSError:
    print("%s not found, MS Office detection may not work properly if "
          "file command library is older." % MAGIC_LIBRARY)

# Must be imported *after* the DLL import above
import magic  # isort:skip pylint: disable=wrong-import-order


class _FidoReader(Fido):
    """Fido wrapper to get pronom code, mimetype and version."""

    # Global variable in Fido
    # pylint: disable=invalid-name, global-statement
    # pylint: disable=global-variable-not-assigned
    global defaults

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
        Fido.__init__(self, quiet=True, format_files=[
            "formats-v94.xml", "format_extensions.xml"])

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
        """Initialize detector."""
        self._puid = None
        super(FidoDetector, self).__init__(filename, mimetype=mimetype,
                                           version=version)

    def detect(self):
        """Detect file format and version."""
        fido = _FidoReader(self.filename)
        fido.identify()
        self.mimetype = fido.mimetype
        self.version = fido.version
        self._puid = fido.puid
        self.info = {"class": self.__class__.__name__,
                     "messages": [],
                     "errors": []}

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
        magic_ = magic.open(magic.MAGIC_MIME_TYPE)
        magic_.load()
        mimetype = magic_.file(encode_path(self.filename))
        magic_.close()
        if mimetype in MIMETYPE_DICT:
            self.mimetype = MIMETYPE_DICT[mimetype]
        else:
            self.mimetype = six.text_type(mimetype)
        self.info = {"class": self.__class__.__name__,
                     "messages": [],
                     "errors": []}

    def get_important(self):
        """
        Important mime types.

        If user has not given a MIME type, we will prefer file detector with
        the following mimetypes:
            - application/x-internet-archive
            - application/vnd.oasis.opendocument.formula

        :returns: A dict possibly containing key "mimetype"
        """
        important = {}
        if (not self._given_mimetype and self.mimetype in
                ["application/x-internet-archive",
                 "application/vnd.oasis.opendocument.formula"]):
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
                     "errors": []}

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
        cmd = [VERAPDF_PATH, encode_path(self.filename)]
        shell = Shell(cmd)

        # Test if the file is a PDF/A
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
        self.version = "A{}".format(version.lower())
        self.mimetype = "application/pdf"
        self.info = {"class": self.__class__.__name__,
                     "messages": ["PDF/A version detected by veraPDF."],
                     "errors": []}

    def _set_info_not_pdf_a(self, error_shell=None):
        """
        Set info to reflect the fact that the file was not a PDF/A.

        :error_shell: If a Shell instance is given, its stderr is
                      set as 'errors' in the info.
        """
        self.info = {"class": self.__class__.__name__,
                     "messages": ["File is not PDF/A, veraPDF detection not "
                                  "needed"],
                     "errors": []}
        if error_shell:
            self.info["errors"] = [error_shell.stderr]

    def get_important(self):
        """
        If and only if this detector determined a file type, it is important.

        This is to make sure that the PDF/A detection result overrides the
        non-archival result obtained by other detectors.
        """
        if self.mimetype and self.version:
            return {"mimetype": self.mimetype, "version": self.version}
        return {}
