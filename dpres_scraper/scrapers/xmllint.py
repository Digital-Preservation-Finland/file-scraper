""" Class for XML file validation with Xmllint. """

import os
import subprocess
import tempfile
try:
    from lxml import etree
except ImportError:
    pass

from dpres_scraper.base import BaseScraper

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

    _supported = {'text/xml': []}
    _only_wellformed = True

    def __init__(self, mimetype, filename, validation):
        self._schema = None
        self._used_version = None
        self._has_constructed_schema = False
        super(Xmllint, self).__init__(mimetype, filename, validation)

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
            self._used_version = tree.docinfo.xml_version
            fd.close()
        except etree.XMLSyntaxError as exception:
            self.errors("Validation failed: document is not well-formed.")
            self.errors(str(exception))
            self._collect_elements()
            return
        except IOError as exception:
            self.errors("Validation failed: missing file.")
            self.errors(str(exception))
            self._collect_elements()
            return

        # Try validate against DTD
        if tree.docinfo.doctype:
            (exitcode, stdout, stderr) = self.exec_xmllint(validate=True)

        # Try validate againts XSD
        else:
            if not self._schema:
                self._schema = self.construct_xsd(tree)
                if not self._schema:
                    # No given schema and didn't find included schemas but XML
                    # was well formed.
                    self.messages("Validation success: Document is "
                                  "well-formed but does not contain schema.")
                    self._collect_elements()
                    return

            (exitcode, stdout, stderr) = self.exec_xmllint(schema=self._schema)
        if exitcode == 0:
            self.messages(
                "%s Validation success%s" % (self.filename, stdout))
        else:
            self.errors(stderr)

        # Clean up constructed schemas
        if self._has_constructed_schema:
            os.remove(self._schema)

        self._collect_elements()

    def construct_xsd(self, document_tree):
        """This method constructs one schema file which collects all used
        schemas from given document tree and imports all of them in one file.


        :tree: XML tree (lxml.etree) where XSD is constructed
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
                prefix='dpres-scraper-', suffix='.tmp')
            et = etree.ElementTree(schema_tree)
            et.write(schema)

            self._has_constructed_schema = True

            return schema

        return []

    def exec_xmllint(self, huge=True, no_output=True, no_network=True,
                     validate=False, schema=None):
        """Execute xmllint
        """
        command = ['xmllint']
        command += ['--valid'] if validate else []
        command += ['--huge'] if huge else []
        command += ['--noout'] if no_output else []
        command += ['--nonet'] if no_network else []
        command += ['--catalogs']
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
        See KDKPAS-1190."""
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
        return 'char'
