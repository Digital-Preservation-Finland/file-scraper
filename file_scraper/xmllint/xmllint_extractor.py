"""Class for XML file well-formed check with Xmllint."""

import os
import tempfile
from io import open as io_open
from pathlib import Path

from xml_helpers.utils import iter_elements

from file_scraper.base import BaseExtractor
from file_scraper.shell import Shell
from file_scraper.logger import LOGGER
from file_scraper.utils import ensure_text
from file_scraper.xmllint.xmllint_model import XmllintMeta

try:
    from lxml import etree
except ImportError:
    pass

XSI = "http://www.w3.org/2001/XMLSchema-instance"
XS = "{http://www.w3.org/2001/XMLSchema}"

XSI_SCHEMA_LOCATION = f"{{{XSI}}}schemaLocation"
XSI_NO_NS_SCHEMA_LOCATION = f"{{{XSI}}}noNamespaceSchemaLocation"

SCHEMA_TEMPLATE = b"""<?xml version = "1.0" encoding = "UTF-8"?>
<xs:schema xmlns="http://dummy"
targetNamespace="http://dummy"
xmlns:xs="http://www.w3.org/2001/XMLSchema"
xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
version="1.0"
elementFormDefault="qualified"
attributeFormDefault="unqualified">
</xs:schema>"""


class XmllintExtractor(BaseExtractor):
    """
    Xmllint extractor class.

    This class implements a plugin interface for extractor module and
    checks if XML files are well-formed using Xmllint tool.
    .. seealso:: http://xmlsoft.org/xmllint.html
    """

    _supported_metadata = [XmllintMeta]
    _only_wellformed = True  # Only well-formed check

    def __init__(self, filename: Path, mimetype, version=None, params=None):
        """
        Initialize extractor.

        :filename: File path
        :mimetype: Predefined mimetype
        :version: Predefined version
        :params: Extra parameters needed for the extractor. The parameters are:
                 schema: Schema path, None by default
                 no_network: True if no network connections allowed (default),
                             False will try to fetch schema files from
                             internet.
                 catalog_path: Path to XMLcatalog
        """
        super().__init__(
            filename=filename, mimetype=mimetype, version=version,
            params=params)
        if params is None:
            params = {}
        self._schema = params.get("schema", None)
        self._has_constructed_schema = False
        self._no_network = params.get("no_network", True)
        self._catalog_path = params.get("catalog_path", None)

    def _evaluate_xsd_location(self, location):
        """Determine whether or not the XSD schema is a
        local file in relation to the assigned XML file.

        If local file is found, absolute path will be returned for
        xsd-construction's import purpose. Otherwise return the location as-is.

        Absolute path is required for construct_xsd-function as the temporary
        file's location will differ a lot in related to the current
        self.filename.

        :param location: Given schema location in string.
        :return: Path of the XSD location. If it's local, absolute path.
        """
        # schemaLocation or noNamespaceSchemaLocation is always either
        # direct path or relative path to the XML in question.
        local_location = self.filename.parent / location
        if local_location.is_file():
            return local_location.absolute()
        return location

    def extract(self):
        """
        Check XML file with Xmllint and return a tuple of results.

        Strategy for XML file check is
            1) Try to check syntax by opening file.
            2) If there's DTD specified in file check against that.
            3) If there's no DTD and we have external XSD check againtst
               that.
            4) If there's no external XSD read schemas used in file and do
               check against them with schema catalog.

        :returns: Tuple (status, report, errors) where
            status -- 0 is success, anything else failure
            report -- generated report
            errors -- errors if encountered, else None

        .. seealso:: https://wiki.csc.fi/wiki/KDK/XMLTiedostomuotojenSkeemat
        """
        # Try to check syntax by opening file in XML parser
        try:
            with io_open(self.filename, "rb") as file_:
                parser = etree.XMLParser(dtd_validation=False, no_network=True)
                tree = etree.parse(file_, parser=parser)
        except etree.XMLSyntaxError as exception:
            self._errors.append("Failed: document is not well-formed.")
            self._errors.append(str(exception))
            return
        except OSError as exception:
            self._errors.append("Failed: missing file.")
            self._errors.append(str(exception))
            return

        # Try check against DTD
        if tree.docinfo.doctype:
            (exitcode, stdout, stderr) = self.exec_xmllint(dtd_check=True)

        # Try check againts XSD
        else:
            if not self._schema:
                self._schema = self.construct_xsd()
                if not self._schema:
                    # No given schema and didn't find included schemas but XML
                    # was well formed.
                    self._messages.append("Success: Document is well-formed "
                                          "but does not contain schema.")
                    self.streams = list(self.iterate_models(
                        well_formed=self.well_formed, tree=tree))
                    self._check_supported()
                    return

            (exitcode, stdout, stderr) = self.exec_xmllint(schema=self._schema)

        # Clean up constructed file before evaluating the exitcode.
        if self._has_constructed_schema:
            os.remove(self._schema)

        if exitcode == 0:
            self._messages.append(
                f"{self.filename} Success\n{stdout}"
            )
        else:
            self._errors += stderr.splitlines()
            return

        self.streams = list(self.iterate_models(
            well_formed=self.well_formed, tree=tree))
        self._check_supported()

    def construct_xsd(self):
        """
        Construct one schema file for the given document.

        The schema file will be placed temporarily in a temporary directory.

        :returns: Path to the constructed XSD schema
        """
        xsd_exists = False

        parser = etree.XMLParser(dtd_validation=False, no_network=True)
        schema_tree = etree.XML(SCHEMA_TEMPLATE, parser)

        elements = iter_elements(str(self.filename))
        for element in elements:
            schema_location = element.attrib.get(XSI_SCHEMA_LOCATION)

            if schema_location:
                xsd_exists = True
                namespaces_locations = schema_location.strip().split()
                # Import all found namespace/schema location pairs
                for namespace, location in zip(
                        *[iter(namespaces_locations)] * 2):
                    xs_import = etree.Element(XS + "import")
                    xs_import.attrib["namespace"] = namespace
                    xs_import.attrib["schemaLocation"] = (
                        str(self._evaluate_xsd_location(location)))
                    schema_tree.append(xs_import)

        elements = iter_elements(str(self.filename))
        for element in elements:
            schema_location = element.attrib.get(XSI_NO_NS_SCHEMA_LOCATION)
            if schema_location:
                xsd_exists = True
                xs_import = etree.Element(XS + "import")
                xs_import.attrib["schemaLocation"] = str(
                    self._evaluate_xsd_location(schema_location))
                schema_tree.append(xs_import)

        if xsd_exists:
            # Construct the schema
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
        command += ["--catalogs"] if self._catalog_path else []
        command += ["--schema", schema] if schema else []
        command += [self.filename]

        if self._catalog_path is not None:
            environment = {
                "SGML_CATALOG_FILES": self._catalog_path
            }
        else:
            environment = {
                "SGML_CATALOG_FILES": "/etc/xml/catalog"
            }

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
            LOGGER.debug("Discarding harmless error '%s'", error)
            self._errors.remove(error)
        for error in errors_to_add:
            self._errors.append(error)

        return super().errors()

    def tools(self):
        """
        Overwriting baseclass implementation
        to collect information about software used by the extractor

        :returns: a dictionary with the used software or UNAV.
        """
        # Version consists of 4 values. Expect the first 3 to follow SemVers
        major, minor, patch, extra = etree.LXML_VERSION
        return {
            "lxml": {"version": f"{major}.{minor}.{patch}.{extra}"}
        }
