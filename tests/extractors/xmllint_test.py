"""
Xmllint extractor tests

This module tests that:
    - MIME type, version, streams and well-formedness of xml files are scraped
      correctly and extractor messages do not contain "<note>".
    - For a well-formed document without schema, extractor messages contains
      "Document is well-formed but does not contain schema."
    - For other well-formed files, extractor messages contains "Success".
    - For file with missing closing tag, extractor messages contains "Opening
      and ending tag mismatch".
    - For invalid given schema and a file without schema, extractor errors
      contains "Schemas validity error".
    - For invalid given schema and a valid file with schema, extractor errors
      contains "parser error".
    - For invalid file with local catalog, extractor errors contains "Missing
      child element(s)".
    - For invalid file with DTD, extractor errors contains "does not follow the
      DTD".
    - For empty file, extractor errors contains "Document is empty".
    - XML files without the header can be reported as well-formed.

    - MIME type text/xml with version 1.0 or None is supported when well-
      formedness is checked.
    - When well-formedness is not checked, text/xml 1.0 is not supported.
    - A made up MIME type is not supported, but version is.

    - Schema and catalogs can be defined as parameters.
"""

import os
import subprocess
from pathlib import Path
import pytest

from file_scraper.xmllint.xmllint_extractor import XmllintExtractor
from tests.common import (parse_results, partial_message_included)

ROOTPATH = os.path.abspath(os.path.join(
    os.path.dirname(__file__), "..", ".."))


@pytest.mark.parametrize(
    ["filename", "result_dict", "params"],
    [
        ("valid_1.0_well_formed.xml", {
            "purpose": "Test valid file without schema.",
            "stdout_part": "Document is well-formed but does not contain "
                           "schema.",
            "stderr_part": ""},
         {}),
        ("valid_1.0_local_xsd.xml", {
            "purpose": "Test valid xml with given schema.",
            "stdout_part": "Success",
            "stderr_part": ""},
         {"schema": os.path.join(
             ROOTPATH, "tests/data/text_xml/supplementary/local.xsd")}),
        ("valid_1.0_catalog.xml", {
            "purpose": "Test valid file with local catalog.",
            "stdout_part": "Success",
            "stderr_part": ""},
         {"catalog_path":
              "tests/data/text_xml/supplementary/catalog_to_local_xsd.xml"}),
        ("valid_1.0_catalog.xml", {
            "purpose": "Test catalog order priority.",
            "stdout_part": "Success",
            "stderr_part": ""},
         {"catalog_path":
              "tests/data/text_xml/supplementary/catalog_with_catalogs.xml"}),
        ("valid_1.0_no_namespace_catalog.xml", {
            "purpose": "Test that no-namespace catalog would work",
            "stdout_part": "Success",
            "stderr_part": ""},
         {"catalog_path": ("tests/data/text_xml/supplementary/"
                           "catalog_to_local_no_namespace_xsd.xml")}),
        ("valid_1.0_dtd.xml", {
            "purpose": "Test valid xml with dtd.",
            "stdout_part": "Success",
            "stderr_part": ""},
         {}),
        ("valid_1.0_mets_noheader.xml", {
            "purpose": "Test valid file without XML header.",
            "stdout_part": "Success",
            "stderr_part": ""},
         {}),
        ("valid_1.0_addml.xml", {
            "purpose": "Test local XSD schema import and validation works",
            "stdout_part": "Success",
            "stderr_part": ""},
         {}),
        ("valid_1.0_no_namespace_xsd.xml", {
            "purpose": "Test local no namespace XSD",
            "stdout_part": "Success",
            "stderr_part": ""},
         {})
    ]
)
def test_extractor_valid(filename, result_dict, params, evaluate_extractor):
    """
    Test extractor with valid files.

    :filename: Test file name
    :result_dict: Result dict containing test purpose, and parts of
                  expected results of stdout and stderr
    :params: Extra parameters for Extractor
    """
    correct = parse_results(filename, "text/xml",
                            result_dict, True, params)
    extractor = XmllintExtractor(filename=Path(correct.filename),
                               mimetype="text/xml",
                               params=correct.params)
    extractor.extract()

    if not correct.well_formed:
        assert not extractor.well_formed
        assert not extractor.streams
        assert partial_message_included(correct.stdout_part,
                                        extractor.messages())
        assert partial_message_included(correct.stderr_part, extractor.errors())
    else:
        evaluate_extractor(extractor, correct)
    assert not partial_message_included("<note>", extractor.messages())


@pytest.mark.parametrize(
    ["filename", "result_dict", "params"],
    [
        ("invalid_1.0_no_closing_tag.xml", {
            "purpose": "Test invalid file without schema.",
            "stdout_part": "",
            "stderr_part": "Opening and ending tag mismatch"},
         {}),
        ("invalid_1.0_local_xsd.xml", {
            "purpose": "Test invalid xml with given schema.",
            "stdout_part": "",
            "stderr_part": "Schemas validity error"},
         {"schema": os.path.join(
             ROOTPATH, "tests/data/text_xml/supplementary/local.xsd")}),
        ("valid_1.0_local_xsd.xml", {
            "purpose": "Test valid xml with given invalid schema.",
            "inverse": True,
            "stdout_part": "",
            "stderr_part": "parser error"},
         {"schema": os.path.join(
             ROOTPATH, "tests/data/text_xml/invalid_local.xsd")}),
        ("invalid_1.0_addml.xml", {
            "purpose": "Test invalid XML against local XSD",
            "stdout_part": "",
            "stderr_part": "Schemas validity error"},
         {}),
        ("invalid_1.0_catalog.xml", {
            "purpose": "Test invalid file with local catalog.",
            "stdout_part": "",
            "stderr_part": "Missing child element(s)"},
         {"catalog_path":
              "tests/data/text_xml/supplementary/catalog_to_local_xsd.xml"}),
        ("valid_1.0_no_namespace_catalog.xml", {
            "purpose": "Test catalog priority.",
            "stdout_part": "",
            "stderr_part": "Schemas validity error"},
         {"catalog_path":
              "tests/data/text_xml/supplementary/catalog_with_catalogs.xml"}),
        ("invalid_1.0_dtd.xml", {
            "purpose": "Test invalid xml with dtd.",
            "stdout_part": "",
            "stderr_part": "does not follow the DTD"},
         {}),
        ("invalid_1.0_no_namespace_xsd.xml", {
            "purpose": "Test invalid XML against local no namespace XSD",
            "stdout_part": "",
            "stderr_part": "Missing child element(s)"},
         {}),
        ("invalid__empty.xml", {
            "purpose": "Test empty xml.",
            "stdout_part": "",
            "stderr_part": "Document is empty"}, {}),
        ("invalid_1.0_diacritics_in_schema_path.xml", {
            "purpose": ("Test invalid file due to diacritics in "
                        "local schema path."),
            "stdout_part": "",
            "stderr_part": ("No matching global declaration available for "
                            "the validation root.")},
         {"catalog_path": ("tests/data/text_xml/supplementary/"
                           "catalog_to_local_xsd_diacritics.xml")}),
    ]
)
def test_extractor_invalid(filename, result_dict, params, evaluate_extractor):
    """
    Test extractor with invalid files.

    :filename: Test file name
    :result_dict: Result dict containing test purpose, and parts of
                  expected results of stdout and stderr
    :params: Extra parameters for Extractor
    """
    correct = parse_results(filename, "text/xml",
                            result_dict, True, params)
    extractor = XmllintExtractor(filename=Path(correct.filename),
                               mimetype="text/xml",
                               params=correct.params)
    extractor.extract()
    if any(item in filename for item in ["empty",
                                         "no_closing_tag",
                                         "no_namespace_catalog",
                                         "diacritics"]):
        correct.well_formed = False
        correct.version = None
        correct.streams[0]["version"] = None

    if not correct.well_formed:
        assert not extractor.well_formed
        assert not extractor.streams
        assert partial_message_included(correct.stdout_part,
                                        extractor.messages())
        assert partial_message_included(correct.stderr_part, extractor.errors())
    else:
        evaluate_extractor(extractor, correct)
    assert not partial_message_included("<note>", extractor.messages())


def test_is_supported():
    """Test is_supported method."""
    mime = "text/xml"
    ver = "1.0"
    assert XmllintExtractor.is_supported(mime, ver, True)
    assert XmllintExtractor.is_supported(mime, None, True)
    assert not XmllintExtractor.is_supported(mime, ver, False)
    assert XmllintExtractor.is_supported(mime, "foo", True)
    assert not XmllintExtractor.is_supported("foo", ver, True)


def test_parameters():
    """Test that parameters and default values work properly."""
    # pylint: disable=protected-access
    extractor = XmllintExtractor(Path("testsfile"), "test/mimetype")
    assert extractor._schema is None
    assert extractor._catalog_path is None

    extractor = XmllintExtractor(
        filename=Path("testsfile"), mimetype="text/xml",
        params={"schema": "schemafile"})
    assert extractor._schema == "schemafile"

    extractor = XmllintExtractor(filename=Path("testsfile"),
                               mimetype="text/xml",
                               params={"catalog_path": "catpath"})
    assert extractor._catalog_path == "catpath"


def test_tools():
    """Test that extractor returns correct version"""
    extractor = XmllintExtractor(filename=Path(""), mimetype="")
    assert extractor.tools()["lxml"]["version"].replace(".", "").isnumeric()


def test_no_network(monkeypatch):
    old_popen_init = subprocess.Popen.__init__

    def _new_popen_init(self, args, stdout, stderr, stdin, shell, env):
        """
        Arguments are taken from file_scraper.shell.Shell.popen()'s calling arguments
        """
        assert "--nonet" in args
        return old_popen_init(self=self, args=args, stdin=stdin, stdout=stdout,
                              stderr=stderr, shell=shell, env=env)

    monkeypatch.setattr(subprocess.Popen, "__init__", _new_popen_init)

    extractor = XmllintExtractor(
        Path("tests/data/text_xml/valid_1.0_gpx_1.0.xml"), "text/xml")
    extractor.extract()
    assert extractor.well_formed
