# Common boilerplate
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
import testcommon.settings

import pytest
# Module to test
import ipt.validator.xmllint


ROOTPATH = os.path.abspath(os.path.join(
    os.path.dirname(__file__),
    '../../../'))
SHAREPATH = os.path.join(ROOTPATH, 'include/share')
OBJECT_CATALOGPATH = os.path.join(
    SHAREPATH,
    'xmlobjectcatalog/catalog-local.xml')
SCHEMAPATH = os.path.join(SHAREPATH, 'schema/mets/mets.xsd')


class TestXmllintValidation:

    @pytest.mark.usefixtures("monkeypatch_Popen")
    @pytest.mark.parametrize(
        ["filename", "schema"],
        [
            ("06_mets_validation/sips/CSC_test001/mets.xml", True),
            ("06_mets_validation/sips/fd2009-00002919-preservation/mets.xml", True),
            ("02_filevalidation_data/xml/catalog_schema_valid.xml", False),
            ("02_filevalidation_data/xml/valid_xsd.xml", False),
            ("02_filevalidation_data/xml/valid_wellformed.xml", False),
            ("02_filevalidation_data/xml/valid_dtd.xml", False),
        ])
    def test_validation_valid(self, filename, schema, capsys):
        """
        test valid cases
        """
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
        assert validator.is_valid
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
            ("02_filevalidation_data/xml/invalid_dtd.xml")
        ])
    def test_validation_invalid(self, filename, capsys):
        """
        test valid cases
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

