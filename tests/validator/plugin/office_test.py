"""
Tests for Office validator.
"""

import os

from ipt.validator.office import Office

BASEPATH = "tests/data/02_filevalidation_data/office"

FILEINFO = {
    "filename": "",
    "format": {
        "mimetype": ""
    }
}


def test_odf_text_ok():
    """
    Test OpenOffice .odt
    """
    FILEINFO["filename"] = os.path.join(BASEPATH, "ODF_Text_Document.odt")
    FILEINFO["format"]['mimetype'] = "application/vnd.oasis.opendocument.text"
    validator = Office(FILEINFO)
    validator.validate()
    assert validator.is_valid


def test_msword_binary_ok():
    """
    Test MS Word binary
    """
    FILEINFO["filename"] = os.path.join(BASEPATH, "MS_Word_97-2003.doc")
    FILEINFO["format"]['mimetype'] = "application/msword"
    validator = Office(FILEINFO)
    validator.validate()
    assert 'Error' not in validator.messages()
    assert validator.messages() != ""
    assert validator.errors() == ""
    assert validator.is_valid


def test_office_open_xml_text_ok():
    """
    Test Office Open XML Text
    """
    FILEINFO["filename"] = os.path.join(BASEPATH, "Office_Open_XML_Text.docx")
    FILEINFO["format"]['mimetype'] = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    validator = Office(FILEINFO)
    validator.validate()
    assert validator.is_valid


def test_odf_presentation_ok():
    """
    Test OpenOffice .odp
    """
    FILEINFO["filename"] = os.path.join(BASEPATH, "ODF_Presentation.odp")
    FILEINFO["format"]['mimetype'] = "application/vnd.oasis.opendocument.presentation"
    validator = Office(FILEINFO)
    validator.validate()
    assert validator.is_valid

def test_mspowerpoint_binary_ok():
    """
    Test MS Power Point binary
    """
    FILEINFO["filename"] = os.path.join(BASEPATH, "MS_PowerPoint_97-2003.ppt")
    FILEINFO["format"]['mimetype'] = "application/vnd.ms-powerpoint"
    validator = Office(FILEINFO)
    validator.validate()
    assert validator.is_valid


def test_office_open_xml_presentation_ok():
    """
    Test Office Open XML presentation
    """
    FILEINFO["filename"] = os.path.join(BASEPATH, "Office_Open_XML_Presentation.pptx")
    FILEINFO["format"]['mimetype'] = "application/vnd.openxmlformats-officedocument.presentationml.presentation"
    validator = Office(FILEINFO)
    validator.validate()
    assert validator.is_valid


def test_odf_spreadsheet():
    """
    Test OpenOffice .ods
    """
    FILEINFO["filename"] = os.path.join(BASEPATH, "ODF_Spreadsheet.ods")
    FILEINFO["format"]['mimetype'] = "application/vnd.oasis.opendocument.spreadsheet"
    validator = Office(FILEINFO)
    validator.validate()
    assert validator.is_valid


def test_msexcel_binary_ok():
    """
    Test MS Excel binary
    """
    FILEINFO["filename"] = os.path.join(BASEPATH, "MS_Excel_97-2003.xls")
    FILEINFO["format"]['mimetype'] = "application/vnd.ms-excel"
    validator = Office(FILEINFO)
    validator.validate()
    assert validator.is_valid


def test_office_open_xml_spreadsheet_ok():
    """
    Test Office Open XML Spreadsheet
    """
    FILEINFO["filename"] = os.path.join(BASEPATH, "Office_Open_XML_Spreadsheet.xlsx")
    FILEINFO["format"]['mimetype'] = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    validator = Office(FILEINFO)
    validator.validate()
    assert validator.is_valid


def test_excel_online_spreadsheet_ok():
    """
    Test  XML Spreadsheet created with Excel Online
    """
    FILEINFO["filename"] = os.path.join(BASEPATH, "Excel_Online_Spreadsheet.xlsx")
    FILEINFO["format"]['mimetype'] = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    validator = Office(FILEINFO)
    validator.validate()
    assert validator.is_valid


def test_odf_graphics():
    """
    Test OpenOffice .odg
    """
    FILEINFO["filename"] = os.path.join(BASEPATH, "ODF_Drawing.odg")
    FILEINFO["format"]['mimetype'] = "application/vnd.oasis.opendocument.graphics"
    validator = Office(FILEINFO)
    validator.validate()
    assert validator.is_valid


def test_odf_formula():
    """
    Test OpenOffice .odf
    """
    FILEINFO["filename"] = os.path.join(BASEPATH, "ODF_Formula.odf")
    FILEINFO["format"]['mimetype'] = "application/vnd.oasis.opendocument.formula"
    validator = Office(FILEINFO)
    validator.validate()
    assert validator.is_valid


def test_msword_empty_file():
    """
    Test empty file
    """
    FILEINFO["filename"] = os.path.join(BASEPATH, "empty_file.doc")
    FILEINFO["format"]['mimetype'] = "application/msword"
    validator = Office(FILEINFO)
    validator.validate()
    assert not validator.is_valid


def test_wrong_mime():
    """
    Test wrong file format
    """
    FILEINFO["filename"] = os.path.join(BASEPATH, "ODF_Text_Document.odt")
    FILEINFO["format"]['mimetype'] = "application/msword"
    validator = Office(FILEINFO)
    validator.validate()
    assert not validator.is_valid


def test_openoffice_corrupted():
    """
    Test corrupted openoffice file
    """
    FILEINFO["filename"] = os.path.join(BASEPATH, "ODF_Text_Document_corrupted.odt")
    FILEINFO["format"]['mimetype'] = "application/vnd.oasis.opendocument.text"
    validator = Office(FILEINFO)
    validator.validate()
    assert not validator.is_valid


def test_fake_msoffice_document():
    """
    Test .odt renamed to .doc
    """
    FILEINFO["filename"] = os.path.join(BASEPATH, "ODF_Text_Document_with_wrong_filename_extension.doc")
    FILEINFO["format"]['mimetype'] = "application/msword"
    validator = Office(FILEINFO)
    validator.validate()
    assert not validator.is_valid


def test_zip_archive():
    """
    Test zip-archive renamed to .docx
    """
    FILEINFO["filename"] = os.path.join(BASEPATH, "MS_Word_2007-2013_XML_zip.docx")
    FILEINFO["format"]['mimetype'] = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    validator = Office(FILEINFO)
    validator.validate()
    assert not validator.is_valid


