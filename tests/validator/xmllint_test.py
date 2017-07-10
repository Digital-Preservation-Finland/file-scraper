# Common boilerplate
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import testcommon.settings

import pytest
# Module to test
import ipt.validator.xmllint


ROOTPATH = os.path.abspath(os.path.join(
    os.path.dirname(__file__), '../../../'))
SCHEMAPATH = "/etc/xml/dpres-xml-schemas/schema_catalogs/schemas/mets/mets.xsd"


@pytest.mark.usefixtures("monkeypatch_Popen")
@pytest.mark.parametrize(
    ["filename", "schema"],
    [
        ("mets/mets.xml", True),
        ("02_filevalidation_data/xml/catalog_schema_valid.xml", False),
        ("02_filevalidation_data/xml/valid_xsd.xml", False),
        ("02_filevalidation_data/xml/valid_wellformed.xml", False),
        ("02_filevalidation_data/xml/valid_dtd.xml", False),
    ])
def test_validation_valid(filename, schema, monkeypatch, capsys):
    """
    test valid cases
    """
    # catalog_path = ('tests/data/test-catalog.xml')
    # monkeypatch.setenv("SGML_CATALOG_FILES", catalog_path)

    fileinfo = {
        "filename": os.path.join(
            testcommon.settings.TESTDATADIR, filename),
        "format": {
            "mimetype": "text/xml",
            "version": "1.0"
        },
    }

    if schema is True:
        fileinfo["schema"] = SCHEMAPATH

    validator = ipt.validator.xmllint.Xmllint(fileinfo)

    validator.validate()
    print capsys.readouterr()
    assert validator.is_valid, "validator errors: %s" % validator.errors()
    assert "Validation success" in validator.messages()
    assert validator.errors() == ""
    # xmllint is using --noout, so the METS XML should not be printed to
    # stdout (KDKPAS-1190)
    assert "mets:mets" not in validator.messages()


@pytest.mark.usefixtures("monkeypatch_Popen")
@pytest.mark.parametrize(
    "filename",
    [
        ("02_filevalidation_data/xml/catalog_schema_invalid.xml"),
        ("02_filevalidation_data/xml/invalid_xsd.xml"),
        ("02_filevalidation_data/xml/invalid_wellformed.xml"),
        ("02_filevalidation_data/xml/invalid_dtd.xml"),
        ("this_file_does_not_exist")
    ])
def test_validation_invalid(filename, capsys):
    """
    test invalid cases
    """
    fileinfo = {
        "filename": os.path.join(
            testcommon.settings.TESTDATADIR, filename),
        "format": {
            "mimetype": "text/xml",
            "version": "1.0"
        },
    }

    validator = ipt.validator.xmllint.Xmllint(fileinfo)

    validator.validate()
    print capsys.readouterr()
    assert not validator.is_valid

    # xmllint is using --noout, so the METS XML should not be printed to
    # stdout (KDKPAS-1190)
    assert "mets:mets" not in validator.messages()
