""" Class for XML file validation with Xmllint. """

import os
import subprocess
import tempfile
try:
    from lxml import etree
except ImportError:
    pass

from file_scraper.base import BaseScraper

XSI = 'http://www.w3.org/2001/XMLSchema-instance'
XS = '{http://www.w3.org/2001/XMLSchema}'

SCHEMA_TEMPLATE = """<?xml version = "1.0" encoding = "UTF-8"?>
    <xs:schema xmlns="http://dummy"
    targetNamespace="http://dummy"
    xmlns:xs="http://www.w3.org/2001/XMLSchema"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    version="1.0"
    elementFormDefault="qualified"
    attributeFormDefault="unqualified">
    </xs:schema>"""


class Xmllint(BaseScraper):
    """This class implements a plugin interface for scraper module and
    validates XML files using Xmllint tool.
    .. seealso:: http://xmlsoft.org/xmllint.html
    """

    _supported = {'text/xml': ['1.0']}  # Supported mimetype
    _only_wellformed = True             # Only well-formed check

    def __init__(self, filename, mimetype, validation=True, params=None):
        """Initialize scraper.
        :filename: File path
        :mimetype: Predicted mimetype of the file
        :validation: True for the full validation, False for just
                     identification and metadata scraping
        :params: Extra parameters needed for the scraper
        """
        if params is None:
            params = {}
        self._schema = params.get('schema')
        self._has_constructed_schema = False
        self._catalogs = params.get('catalogs', True)
        self._no_network = params.get('no_network', True)
        super(Xmllint, self).__init__(filename, mimetype, validation, params)

    @classmethod
    def is_supported(cls, mimetype, version=None,
                     validation=True, params=None):
        """This is not a Schematron validator
        :mimetype: Identified mimetype
        :version: Identified version (if needed)
        :validation: True for the full validation, False for just
                     identification and metadata scraping
        :params: Extra parameters needed for the scraper
        :returns: True if scraper is supported
        """
        if params is None:
            params = {}
        if 'schematron' in params:
            return False
        return super(Xmllint, cls).is_supported(mimetype, version,
                                                validation, params)

    def scrape_file(self):
        """Validate XML file with Xmllint and return a tuple of results.
        Strategy for XML file validation is
            1) Try validate well-formedness by opening file.
            2) If there's DTD specified in file do DTD validation
            3) If there's no DTD and we have external XSD do validation againts
               that.
            4) If there's no external XSD read schemas used in file and do
               validation againts them with schema catalog.

        :returns: Tuple (status, report, errors) where
            status -- 0 is success, anything else failure
            report -- generated report
            errors -- errors if encountered, else None

        .. seealso:: https://wiki.csc.fi/wiki/KDK/XMLTiedostomuotojenSkeemat
        """

        # Try to validate well-formedness by opening file in XML parser
        try:
            fd = open(self.filename)
            parser = etree.XMLParser(dtd_validation=False, no_network=True)
            tree = etree.parse(fd, parser=parser)
            self.version = tree.docinfo.xml_version
            fd.close()
        except etree.XMLSyntaxError as exception:
            self.errors("Scraping failed: document is not well-formed.")
            self.errors(str(exception))
            self._collect_elements()
            return
        except IOError as exception:
            self.errors("Scraping failed: missing file.")
            self.errors(str(exception))
            self._collect_elements()
            return

        # Try validate against DTD
        if tree.docinfo.doctype:
            (exitcode, stdout, stderr) = self.exec_xmllint(dtd_validate=True)

        # Try validate againts XSD
        else:
            if not self._schema:
                self._schema = self.construct_xsd(tree)
                if not self._schema:
                    # No given schema and didn't find included schemas but XML
                    # was well formed.
                    self.messages("Scraping success: Document is "
                                  "well-formed but does not contain schema.")
                    self._collect_elements()
                    return

            (exitcode, stdout, stderr) = self.exec_xmllint(schema=self._schema)
        if exitcode == 0:
            self.messages(
                "%s Scraping success%s" % (self.filename, stdout))
        else:
            self.errors(stderr)

        # Clean up constructed schemas
        if self._has_constructed_schema:
            os.remove(self._schema)

        self._check_supported()
        self._collect_elements()

    def construct_xsd(self, document_tree):
        """This method constructs one schema file which collects all used
        schemas from given document tree and imports all of them in one file.
        :idocument_tree: XML tree (lxml.etree) where XSD is constructed
        :returns: Path to the constructed XSD schema
        """

        xsd_exists = False

        parser = etree.XMLParser(dtd_validation=False, no_network=True)
        schema_tree = etree.XML(SCHEMA_TEMPLATE, parser)

        schema_locations = set(document_tree.xpath(
            '//*/@xsi:schemaLocation', namespaces={'xsi': XSI}))
        for schema_location in schema_locations:
            xsd_exists = True

            namespaces_locations = schema_location.strip().split()
            # Import all found namspace/schema location pairs
            for namespace, location in zip(*[iter(namespaces_locations)] * 2):
                xs_import = etree.Element(XS + 'import')
                xs_import.attrib['namespace'] = namespace
                xs_import.attrib['schemaLocation'] = location
                schema_tree.append(xs_import)

        schema_locations = set(document_tree.xpath(
            '//*/@xsi:noNamespaceSchemaLocation', namespaces={'xsi': XSI}))
        for schema_location in schema_locations:
            xsd_exists = True

            # Check if XSD file is included in SIP
            local_schema_location = os.path.dirname(
                self.filename) + '/' + schema_location
            if os.path.isfile(local_schema_location):
                schema_location = local_schema_location

            xs_import = etree.Element(XS + 'import')
            xs_import.attrib['schemaLocation'] = schema_location
            schema_tree.append(xs_import)
        if xsd_exists:
            # Contstruct the schema
            _, schema = tempfile.mkstemp(
                prefix='file-scraper-', suffix='.tmp')
            et = etree.ElementTree(schema_tree)
            et.write(schema)

            self._has_constructed_schema = True

            return schema

        return []

    def exec_xmllint(self, dtd_validate=False, schema=None):
        """Execute xmllint.
        :dtd_validate: True, if validation against DTD, false otherwise
        :schema: Schema file
        :returns: tuple including: returncode, stdout, strderr
        """
        command = ['xmllint']
        command += ['--valid'] if dtd_validate else []
        command += ['--huge']
        command += ['--noout']
        command += ['--nonet'] if self._no_network else []
        command += ['--catalogs'] if self._catalogs else []
        command += ['--schema', schema] if schema else []
        command += [self.filename]

        proc = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=False)

        (stdout, stderr) = proc.communicate()
        returncode = proc.returncode

        return (returncode, stdout, stderr)

    def errors(self, error=None):
        """Remove the warning which we do not need to see from self.stderr.
        See KDKPAS-1190.
        :error: Error messages
        :returns: Filtered error messages
        """
        if error:
            filtered_errors = []
            for line in error.splitlines():
                if 'this namespace was already imported' in line:
                    continue
                filtered_errors.append(line)
                if 'I/O error : Attempt to load network entity' in line:
                    filtered_errors.append(
                        'ERROR: Schema definition propably missing'
                        'from XML catalog')
            error = "\n".join(filtered_errors)

        return super(Xmllint, self).errors(error)

    # pylint: disable=no-self-use
    def _s_stream_type(self):
        """Return file type
        """
        return 'text'
