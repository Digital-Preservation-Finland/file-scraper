# Common boilerplate
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pytest
# Module to test
import dpres_scraper.scrapers.xmllint


ROOTPATH = os.path.abspath(os.path.join(
    os.path.dirname(__file__), '../../../'))
SCHEMAPATH = "/etc/xml/dpres-xml-schemas/schema_catalogs/schemas/mets/mets.xsd"


@pytest.mark.parametrize(
    ["filename", "schema"],
    [
        ("mets/mets.xml", True),
        ("data/text/catalog_schema_valid.xml", False),
        ("data/text/valid_xsd.xml", False),
        ("data/text/valid_wellformed.xml", False),
        ("data/text/valid_dtd.xml", False),
    ])
def test_scraping_valid(filename, schema, monkeypatch, capsys):
    """
    test valid cases
    """
    # catalog_path = ('tests/data/test-catalog.xml')
    # monkeypatch.setenv("SGML_CATALOG_FILES", catalog_path)
    filepath = os.path.join('tests/data', filename)
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
        ("data/text/catalog_schema_invalid.xml"),
        ("data/text/invalid_xsd.xml"),
        ("data/text/invalid_wellformed.xml"),
        ("data/text/invalid_dtd.xml"),
        ("this_file_does_not_exist")
    ])
def test_scraping_invalid(filename, capsys):
    """
    test invalid cases
    """
    filepath = os.path.join('tests/data', filename)
    scraper = dpres_scraper.scrapers.xmllint.Xmllint(filepath, 'text/xml')

    scraper.scrape_file()
    print capsys.readouterr()
    assert not scraper.well_formed

    # xmllint is using --noout, so the METS XML should not be printed to
    # stdout (KDKPAS-1190)
    assert "mets:mets" not in scraper.messages()
