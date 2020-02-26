"""Class for XML file well-formed check with Xmllint."""
from __future__ import unicode_literals

import os
import tempfile
from io import open as io_open

import six

from file_scraper.base import BaseScraper
from file_scraper.shell import Shell
from file_scraper.utils import ensure_text, decode_path, encode_path
from file_scraper.xmllint.xmllint_model import XmllintMeta

try:
    from lxml import etree
except ImportError:
    pass


XSI = "http://www.w3.org/2001/XMLSchema-instance"
XS = "{http://www.w3.org/2001/XMLSchema}"

SCHEMA_TEMPLATE = b"""<?xml version = "1.0" encoding = "UTF-8"?>
<xs:schema xmlns="http://dummy"
targetNamespace="http://dummy"
xmlns:xs="http://www.w3.org/2001/XMLSchema"
xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
version="1.0"
elementFormDefault="qualified"
attributeFormDefault="unqualified">
</xs:schema>"""


class XmllintScraper(BaseScraper):
    """
    Xmllint scraper class.

    This class implements a plugin interface for scraper module and
    checks if XML files are well-formed using Xmllint tool.
    .. seealso:: http://xmlsoft.org/xmllint.html
    """

    _supported_metadata = [XmllintMeta]
    _only_wellformed = True  # Only well-formed check

    def __init__(self, filename, mimetype, version=None,
                 check_wellformed=True, params=None):
        """
        Initialize scraper.

        :filename: File path
        :check_wellformed: True for the full well-formed check, False for just
                           detection and metadata scraping
        :params: Extra parameters needed for the scraper
        """
        if params is None:
            params = {}
        self._schema = params.get("schema", None)
        self._has_constructed_schema = False
        self._catalogs = params.get("catalogs", True)
        self._no_network = params.get("no_network", True)
        self._catalog_path = params.get("catalog_path", None)
        super(XmllintScraper, self).__init__(
            filename=filename, mimetype=mimetype, version=version,
            check_wellformed=check_wellformed, params=params)

    @classmethod
    def is_supported(cls, mimetype, version=None,
                     check_wellformed=True, params=None):
        """
        Return True if MIME type and version are supported.

        This is not a Schematron scraper, so if params contain "schematron",
        False is returned.

        :mimetype: Identified mimetype
        :version: Identified version (if needed)
        :check_wellformed: True for the full well-formed check, False for just
                           detection and metadata scraping
        :params: Extra parameters needed for the scraper
        :returns: True if scraper is supported
        """
        if params is None:
            params = {}
        if "schematron" in params:
            return False
        return super(XmllintScraper, cls).is_supported(mimetype, version,
                                                       check_wellformed,
                                                       params)

    def scrape_file(self):
        """
        Check XML file with Xmllint and return a tuple of results.

        Strategy for XML file check is
            1) Try to check syntax by opening file.
            2) If there's DTD specified in file check against that.
            3) If there's no DTD and we have external XSD check againtst
               that.
            4) If there's no external XSD read schemas used in file and do
               check againts them with schema catalog.

        :returns: Tuple (status, report, errors) where
            status -- 0 is success, anything else failure
            report -- generated report
            errors -- errors if encountered, else None

        .. seealso:: https://wiki.csc.fi/wiki/KDK/XMLTiedostomuotojenSkeemat
        """
        if not self._check_wellformed and self._only_wellformed:
            self._messages.append("Skipping scraper: Well-formed check not "
                                  "used.")
            return
        # Try to check syntax by opening file in XML parser
        try:
            file_ = io_open(self.filename, "rb")
            parser = etree.XMLParser(dtd_validation=False, no_network=True)
            tree = etree.parse(file_, parser=parser)
            file_.close()
        except etree.XMLSyntaxError as exception:
            self._errors.append("Failed: document is not well-formed.")
            self._errors.append(six.text_type(exception))
            return
        except IOError as exception:
            self._errors.append("Failed: missing file.")
            self._errors.append(six.text_type(exception))
            return

        # Try check against DTD
        if tree.docinfo.doctype:
            (exitcode, stdout, stderr) = self.exec_xmllint(dtd_check=True)

        # Try check againts XSD
        else:
            if not self._schema:
                self._schema = self.construct_xsd(tree)
                if not self._schema:
                    # No given schema and didn"t find included schemas but XML
                    # was well formed.
                    self._messages.append("Success: Document is well-formed "
                                          "but does not contain schema.")
                    self.iterate_models(tree=tree)
                    self._check_supported()
                    return

            (exitcode, stdout, stderr) = self.exec_xmllint(schema=self._schema)

        if exitcode == 0:
            self._messages.append(
                "%s Success\n%s" % (decode_path(self.filename), stdout)
            )
        else:
            self._errors += stderr.splitlines()
            return

        # Clean up constructed schemas
        if self._has_constructed_schema:
            os.remove(self._schema)

        self.iterate_models(tree=tree)
        self._check_supported()

    def construct_xsd(self, document_tree):
        """
        Construct one schema file for the given document tree.

        :returns: Path to the constructed XSD schema
        """

        xsd_exists = False

        parser = etree.XMLParser(dtd_validation=False, no_network=True)
        schema_tree = etree.XML(SCHEMA_TEMPLATE, parser)

        schema_locations = set(document_tree.xpath(
            "//*/@xsi:schemaLocation", namespaces={"xsi": XSI}))
        for schema_location in schema_locations:
            xsd_exists = True

            namespaces_locations = schema_location.strip().split()
            # Import all found namspace/schema location pairs
            for namespace, location in zip(*[iter(namespaces_locations)] * 2):
                xs_import = etree.Element(XS + "import")
                xs_import.attrib["namespace"] = namespace
                xs_import.attrib["schemaLocation"] = location
                schema_tree.append(xs_import)

        schema_locations = set(document_tree.xpath(
            "//*/@xsi:noNamespaceSchemaLocation", namespaces={"xsi": XSI}))
        for schema_location in schema_locations:
            xsd_exists = True

            # Check if XSD file is included in SIP
            local_schema_location = os.path.join(
                os.path.dirname(self.filename),
                encode_path(schema_location)
            )
            if os.path.isfile(local_schema_location):
                schema_location = local_schema_location

            xs_import = etree.Element(XS + "import")
            xs_import.attrib["schemaLocation"] = decode_path(schema_location)
            schema_tree.append(xs_import)
        if xsd_exists:
            # Contstruct the schema
            _, schema = tempfile.mkstemp(
                prefix="file-scraper-", suffix=".tmp")
            elem_tree = etree.ElementTree(schema_tree)
            elem_tree.write(schema)
            self._has_constructed_schema = True

            return schema

        return []

    def exec_xmllint(self, dtd_check=False, schema=None):
        """
        Execute xmllint.

        :dtd_check: True, if check against DTD, false otherwise
        :schema: Schema file
        :returns: tuple including: returncode, stdout, strderr
        """
        command = ["xmllint"]
        command += ["--valid"] if dtd_check else []
        command += ["--huge"]
        command += ["--noout"]
        command += ["--nonet"] if self._no_network else []
        command += ["--catalogs"] if self._catalogs else []
        command += ["--schema", schema] if schema else []
        command += [encode_path(self.filename)]

        if self._catalog_path is not None:
            environment = {
                "SGML_CATALOG_FILES": self._catalog_path
            }
        else:
            environment = None

        shell = Shell(command, env=environment)

        return (shell.returncode, shell.stdout, shell.stderr)

    def errors(self):
        """
        Return errors without unnecessary ones.

        See KDKPAS-1190.

        :returns: Filtered error messages
        """
        errors_to_remove = []
        errors_to_add = []
        for error in self._errors:
            line = ensure_text(error)
            if "this namespace was already imported" in line:
                errors_to_remove.append(error)
            if "I/O error : Attempt to load network entity" in line:
                errors_to_add.append(
                    "Schema definition probably missing from XML catalog")
                errors_to_remove.append(error)
        for error in errors_to_remove:
            self._errors.remove(error)
        for error in errors_to_add:
            self._errors.append(error)

        return super(XmllintScraper, self).errors()
