""" Class for XML file validation with Xmllint. """

import os
import tempfile
import errno
from lxml import etree

from ipt.validator.basevalidator import BaseValidator
from ipt.validator.basevalidator import ValidatorError

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


class Xmllint(BaseValidator):

    """This class implements a plugin interface for validator module and
    validates XML files using Xmllint tool.

    .. seealso:: http://xmlsoft.org/xmllint.html
    """

    def __init__(self, mimetype, fileversion, filename):
        super(Xmllint, self).__init__()

        self.exec_cmd = ['xmllint']
        self.filename = filename
        self.fileversion = fileversion
        self.mimetype = mimetype
        self.schema_path = None
        self.used_version = None
        self.has_constructed_schema = False

        # Prevent network access
        self.exec_cmd += ["--nonet"]

        if mimetype != "text/xml":
            raise ValidatorError("Unknown mimetype: %s" % mimetype)

    def validate(self):
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

        self.exec_cmd += [self.filename]

        try:
            fd = open(self.filename)
            parser = etree.XMLParser(dtd_validation=False, no_network=True)
            tree = etree.parse(fd, parser=parser)
            self.used_version = tree.docinfo.xml_version
            fd.close()
        except IOError as error:
            # if mets.xml is not found in SIP root, it is not a system error
            # case. Instead, it should be interpreted as wrong sip structure.
            if error.errno == errno.ENOENT:
                self.statuscode = 117
                self.stdout = "xml file is missing or mislocated"
                self.stderr = error
                return self.statuscode, self.stdout, self.stderr
            # System error
            raise IOError(error)
        except etree.XMLSyntaxError:
            self.statuscode = 1
            self.stderr = "Validation failed: document is not well formed."
            return self.statuscode, "", self.stderr

        # Try validate against DTD
        if tree.docinfo.doctype:
            self.exec_cmd += ['--valid']
            self.exec_validator()

        # Try validate againts XSD
        else:
            if not self.schema_path:
                schema_path = self.construct_xsd(tree)
                if schema_path:
                    self.add_schema(schema_path)
                else:
                    # No given schema and didn't find included schemas but XML
                    # was well formed.
                    self.statuscode = 0
                    self.stdout = "Validation success: Document is " \
                        "well-formed but does not contain schema."
                    self.stderr = ""
                    return self.statuscode, self.stdout, self.stderr

            self.exec_validator()

            # Clean up constructed schema
            if self.has_constructed_schema:
                os.remove(self.schema_path)
                self.schema_path = None

        return self.statuscode, self.stdout, self.stderr

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
            local_schema_location = os.path.dirname(self.filename) + '/' + \
                schema_location
            if os.path.isfile(local_schema_location):
                schema_location = local_schema_location

            xs_import = etree.Element(XS + 'import')
            xs_import.attrib['schemaLocation'] = schema_location
            schema_tree.append(xs_import)
        if xsd_exists:
            # Contstruct the schema
            fd, schema_path = tempfile.mkstemp(
                prefix='information-package-tools-', suffix='.tmp')
            et = etree.ElementTree(schema_tree)
            et.write(schema_path)

            self.has_constructed_schema = True

            return schema_path

        return False

    def set_catalog(self, catalogpath):
        """ Set XML Catalog for Xmllint """
        self.exec_cmd += ['--catalogs']
        self.environment['SGML_CATALOG_FILES'] = catalogpath

    def add_schema(self, schemapath):
        """Add schema file for validator.

        :schemapath: Path to the schema file
        :returns: No returned values
        """
        self.schema_path = schemapath
        self.exec_cmd += ['--schema', schemapath]

    def check_validity(self):
        """Check validation result of this parser.

        :returns: Tuple (status, report, errors) where
            status -- 0 is success, anything else failure
            report -- generated report
            errors -- errors if encountered, else None

        """
        if self.statuscode is not None:
            return self.statuscode, self.stderr, self.stdout
        return self.validate()

    def check_version(self, version):
        """Check version of given XML document. The version number is in  XML
        document header <?xml version='xx'?> so this method reads the first
        line and queries version string.

        .. note:: XML header is not required and so there might not be a
        version string. If that happens this method returns None.

        .. seelaso:: http://www.w3.org/TR/xml/#sec-prolog-dtd

        :version: Version number to compare with
        :returns: If given version number matches return None, otherwise return
                  an error string.
        """

        if not self.used_version:
            self.validate()

        if self.used_version == version:
            return None

        return "ERROR: File version is '%s', expected '%s'" % (
            self.used_version, version)

    def check_profile(self, profile):
        """XML file format does not have profiles. This is stale method to
        satisfy BaseValidator interface.

        :returns: Returns always None
        """

        return None
