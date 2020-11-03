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

CATALOG_TEMPLATE = b"""<!DOCTYPE catalog PUBLIC "-//OASIS//DTD XML Catalogs V1.0//EN" "catalog.dtd">
<catalog xmlns="urn:oasis:names:tc:entity:xmlns:xml:catalog" prefer="public" xml:base="./">
</catalog>
"""

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

    def __init__(self, filename, mimetype, version=None, params=None):
        """
        Initialize scraper.

        :filename: File path
        :mimetype: Predefined mimetype
        :version: Predefined version
        :params: Extra parameters needed for the scraper. The parameters are:
                 schema: Schema path, None by default
                 catalogs: True if XML catalog used (default), False otherwise
                 no_network: True if no network connections allowed (default),
                             False will try to fetch schema files from
                             internet.
                 catalog_path: Path to XMLcatalog
                 base_path: Base path that is being operated at. Default: "./"
                 additional_catalog_rewrites: Additional rewrite rules to
                    generate an extra temporary catalog from. Provided as
                    dictionary by { uriStartString: rewritePrefix }, where
                    uriStartString is the source and rewritePrefix is the
                    destination. These will not take priority over
                    file provided via catalog_path.

                    base_path will be used as the catalog's base route.
        """
        super(XmllintScraper, self).__init__(
            filename=filename, mimetype=mimetype, version=version,
            params=params)
        if params is None:
            params = {}
        self._schema = params.get("schema", None)
        self._has_constructed_schema = False
        self._catalogs = params.get("catalogs", True)
        self._no_network = params.get("no_network", True)
        self._catalog_path = params.get("catalog_path", None)
        self._base_path = params.get("base_path", "./")
        self._additional_catalog_rewrites = params.get(
            "additional_catalog_rewrites", None)
        self._temporary_catalog_path = None

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

    def _evaluate_xsd_location(self, location):
        """Determine whether or not the XSD schema is a
        local file in relation to the assigned XML file.

        If local file is found, absolute path will be returned for
        xsd-construction's import purpose. Otherwise return the location as-is.

        Absolute path is required for construct_xsd-function as the temporary
        file's location will differ a lot in related to the current
        self.filename.

        :param location: Given schema location in string.
        :return: String of the XSD location. If it's local, absolute path.
        """
        # schemaLocation or noNamespaceSchemaLocation is always either
        # direct path or relative path to the XML in question.
        local_location = os.path.join(
            os.path.dirname(encode_path(self.filename)),
            encode_path(location)
        )
        if os.path.isfile(local_location):
            return os.path.abspath(local_location)
        return location

    def scrape_file(self):
        """
        Check XML file with Xmllint and return a tuple of results.

        Strategy for XML file check is
            1) Try to check syntax by opening file.
            2) If there's DTD specified in file check against that.
            3) If there's no DTD and we have external XSD check againtst
               that.
            4) If there's no external XSD read schemas used in file and do
               check against them with schema catalog.
               4.a) If no additional catalog rewrites are provided, proceed.
               4.b) If additional catalog rewrites are provided, create a
                temporary catalog file that will be added as secondary catalog
                to the default schema catalog.

        :returns: Tuple (status, report, errors) where
            status -- 0 is success, anything else failure
            report -- generated report
            errors -- errors if encountered, else None

        .. seealso:: https://wiki.csc.fi/wiki/KDK/XMLTiedostomuotojenSkeemat
        """
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
                    # No given schema and didn't find included schemas but XML
                    # was well formed.
                    self._messages.append("Success: Document is well-formed "
                                          "but does not contain schema.")
                    self.streams = list(self.iterate_models(
                        well_formed=self.well_formed, tree=tree))
                    self._check_supported()
                    return

            if self._additional_catalog_rewrites:
                self._construct_temporary_catalog_xml()

            (exitcode, stdout, stderr) = self.exec_xmllint(schema=self._schema)

        if exitcode == 0:
            self._messages.append(
                "%s Success\n%s" % (decode_path(self.filename), stdout)
            )
        else:
            self._errors += stderr.splitlines()
            return

        # Clean up constructed files before evaluating the result.
        if self._has_constructed_schema:
            os.remove(self._schema)
        if self._temporary_catalog_path:
            os.remove(self._temporary_catalog_path)

        self.streams = list(self.iterate_models(
            well_formed=self.well_formed, tree=tree))
        self._check_supported()

    def _construct_temporary_catalog_xml(self):
        """Constructs a temporary catalog file filled with given rewrite
        rules.

        Additional rewrite rules are expected to be in dict format::

            {
                rewrite_uri_start_string: rewrite_uri_rewrite_prefix
            }
        """
        parser = etree.XMLParser(dtd_validation=False, no_network=True)
        catalog_tree = etree.XML(CATALOG_TEMPLATE, parser)
        entry_added = False
        for start_string in self._additional_catalog_rewrites:
            rewrite_prefix = self._additional_catalog_rewrites[start_string]
            rewrite_element = etree.Element("rewriteURI")
            rewrite_element.attrib["uriStartString"] = start_string
            rewrite_element.attrib["rewritePrefix"] = rewrite_prefix
            catalog_tree.append(rewrite_element)
            entry_added = True

        if entry_added:
            # We'll set absolute path to the catalog's xml:base and making sure
            # that it'll end with one ending slash.
            for key in catalog_tree.attrib:
                if key.endswith('base'):
                    catalog_tree.attrib[key] = os.path.abspath(
                        self._base_path).rstrip('/') + '/'
                    break
            _, schema = tempfile.mkstemp(prefix="file-scraper-catalog-",
                                         suffix=".tmp")
            elem_tree = etree.ElementTree(catalog_tree)
            elem_tree.write(schema)
            self._temporary_catalog_path = schema

    def construct_xsd(self, document_tree):
        """
        Construct one schema file for the given document tree.

        The schema file will be placed temporarily in a temporary directory.

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
                xs_import.attrib[
                    "schemaLocation"] = self._evaluate_xsd_location(location)
                schema_tree.append(xs_import)

        schema_locations = set(document_tree.xpath(
            "//*/@xsi:noNamespaceSchemaLocation", namespaces={"xsi": XSI}))
        for schema_location in schema_locations:
            xsd_exists = True
            xs_import = etree.Element(XS + "import")
            xs_import.attrib["schemaLocation"] = decode_path(
                self._evaluate_xsd_location(schema_location))
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

        # The order of catalog files matter. The first one has priority if
        # there are rewrite uri duplicates.
        catalog_files = []
        if self._catalog_path is not None:
            catalog_files.append(self._catalog_path)
        if self._temporary_catalog_path is not None:
            catalog_files.append(self._temporary_catalog_path)

        if catalog_files:
            environment = {
                "SGML_CATALOG_FILES": ':'.join(catalog_files)
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
