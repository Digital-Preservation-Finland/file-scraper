# Common boilerplate
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pytest
# Module to test
import dpres_scraper.scrapers.xmllint


ROOTPATH = 'tests/data/text_xml'
SCHEMAPATH = "/etc/xml/dpres-xml-schemas/schema_catalogs/schemas/mets/mets.xsd"


@pytest.mark.parametrize(
    ["filename", "schema"],
    [
        ("valid_1.0.xml", True),
        # ("valid_1.0_mets.xml", True),
        # ("valid_1.0_catalog_schema.xml", False),
        # ("valid_1.0_xsd.xml", False),
        # ("valid_1.0_wellformed.xml", False),
        # ("valid_1.0_dtd.xml", False),
    ])
def test_scraping_valid(filename, schema, monkeypatch, capsys):
    """
    test valid cases
    """
    # catalog_path = ('tests/data/test-catalog.xml')
    # monkeypatch.setenv("SGML_CATALOG_FILES", catalog_path)
    filepath = os.path.join(ROOTPATH, filename)
    scraper = dpres_scraper.scrapers.xmllint.Xmllint(filepath, 'text/xml')

    scraper.scrape_file()
    print capsys.readouterr()
    assert scraper.well_formed, "scraper errors: %s" % scraper.errors()
    assert "Validation success" in scraper.messages()
    assert scraper.errors() == ""
    # xmllint is using --noout, so the METS XML should not be printed to
    # stdout (KDKPAS-1190)
    assert "mets:mets" not in scraper.messages()


@pytest.mark.parametrize(
    "filename",
    [
        ("invalid_1.0_catalog_schema.xml"),
        ("invalid_1.0_xsd.xml"),
        ("invalid_1.0_wellformed.xml"),
        ("invalid_1.0_dtd.xml"),
    ])
def test_scraping_invalid(filename, capsys):
    filepath = os.path.join(ROOTPATH, filename)
    scraper = dpres_scraper.scrapers.xmllint.Xmllint(filepath, 'text/xml')

    scraper.scrape_file()
    print capsys.readouterr()
    assert not scraper.well_formed

    # xmllint is using --noout, so the METS XML should not be printed to
    # stdout (KDKPAS-1190)
    assert "mets:mets" not in scraper.messages()
