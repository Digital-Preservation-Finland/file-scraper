"""Module for validating files with Pythons lxml library """
import os
import re
import subprocess
from lxml import etree

from ipt.validator.basevalidator import BaseValidator

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


class Libxml(BaseValidator):

    """ Initializes lxml validator and set ups everything so that
        methods from base class (BaseValidator) can be called, such as
        validate() for file validation.


        .. seealso:: http://lxml.de
    """

    def __init__(self, mimetype, fileversion, filename):
        super(Libxml, self).__init__()

        self.filename = filename
        self.fileversion = fileversion
        self.mimetype = mimetype

        if mimetype != "text/xml":
            raise Exception("Unknown mimetype: %s" % mimetype)

    def exec_validator(self):
        try:
            f = open(self.filename)
            parser = etree.XMLParser(dtd_validation=False, no_network=True)
            tree = etree.parse(f, parser=parser)
            f.close()
        except IOError as e:
            # System error, do something!
            raise
        except etree.XMLSyntaxError:
            self.statuscode = 1
            self.stderr = "Validation failed: document not well formed"
            return self.statuscode, "", self.stderr

        # Try validate against DTD
        if tree.docinfo.doctype:

            try:
                f = open(self.filename)
                parser = etree.XMLParser(dtd_validation=True,  no_network=True)
                tree = etree.parse(f, parser)
                f.close()
            except etree.XMLSyntaxError as e:
                self.statuscode = 1
                self.stderr = "DTD validation failed"
                return self.statuscode, self.stdout, self.stderr
            else:
                self.statuscode = 0
                self.stdout = "DTD validation success"
                return self.statuscode, self.stdout, self.stderr

        # Try validate againts XSD
        else:
            xsd_exists = False

            parser = etree.XMLParser(dtd_validation=False, no_network=True)
            schema_tree = etree.XML(SCHEMA_TEMPLATE, parser)
            schema_locations = set(tree.xpath("//*/@xsi:schemaLocation",
                                              namespaces={'xsi': XSI}))

            for schema_location in schema_locations:
                xsd_exists = True

                namespaces_locations = schema_location.strip().split()
                # Import all found namspace/schema location pairs
                for namespace, location in \
                        zip(*[iter(namespaces_locations)] * 2):
                    xs_import = etree.Element(XS + "import")
                    xs_import.attrib['namespace'] = namespace
                    xs_import.attrib['schemaLocation'] = location
                    schema_tree.append(xs_import)

            schema_locations = set(
                tree.xpath(
                    "//*/@xsi:noNamespaceSchemaLocation",
                    namespaces={'xsi': XSI}))
            for schema_location in schema_locations:
                xsd_exists = True

                # Check if XSD file is included in SIP
                local_schema_location = os.path.dirname(self.filename) + "/" +\
                    schema_location
                if os.path.isfile(local_schema_location):
                    schema_location = local_schema_location

                xs_import = etree.Element(XS + "import")
                xs_import.attrib['schemaLocation'] = schema_location
                schema_tree.append(xs_import)

            if xsd_exists:
                # Contstruct the schema

                schema = etree.XMLSchema(schema_tree)
                # Validate!
                try:
                    # Read XML file again. This is workaroud for bug explained
                    # in https://jira.csc.fi/browse/KDKPAS-520
                    f = open(self.filename)
                    tree = etree.XML(f.read())
                    f.close()

                    schema.assertValid(tree)
                except IOError as e:
                    # System error, do something!
                    raise
                except etree.DocumentInvalid as error:
                    self.statuscode = 1
                    self.stderr = "XSD validation failed: ", error
                    return self.statuscode, self.stdout, self.stderr
                else:
                    self.statuscode = 0
                    self.stdout = "XSD validation success"
                    return self.statuscode, self.stdout, self.stderr

            self.statuscode = 0
            self.stdout = "Validation success: Document is well-formed but\
                does not contain schemas"
            return self.statuscode, self.stdout, self.stderr

    def check_validity(self):
        if self.statuscode == 0:
            return None
        return ""

    def check_version(self, version):
        """ Check the version of XML document. The version string is located at
            the beginning of the XML document:

            <?xml version="1.0" encoding="UTF-8"?>

            .. note:: The version of number of XML document is not mandatory.
        """

        try:
            file_ = open(self.filename)
            parser = etree.XMLParser(dtd_validation=False, no_network=True)
            tree = etree.parse(file_, parser)
        except:
            return ""
        if version == tree.docinfo.xml_version:
            return None
        return ""

    def check_profile(self, profile):
        """ TODO: Move this away from BaseValidator """
        return None

    def set_catalog(self, catalogpath):
        """
        Set catalogpath.
        """
        pass
        os.environ['XML_CATALOG_FILES'] = catalogpath
