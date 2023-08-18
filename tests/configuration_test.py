"""Tests for config.py."""
import pytest

from file_scraper.config import get_value, read_config


@pytest.fixture(scope="function")
def config_file_fx(monkeypatch):
    """
    Set the environment variable 'FILE_SCRAPER_CONFIG' to a test configuration
    file."""
    monkeypatch.setenv("FILE_SCRAPER_CONFIG", "tests/config/test.conf")


@pytest.fixture(scope="function")
def cleanup_config_dict_fx():
    """Clean up '_config_dict' attribute in 'read_config' function."""
    if hasattr(read_config, "_config_dict"):
        del read_config._config_dict


@pytest.mark.usefixtures("config_file_fx", "cleanup_config_dict_fx")
def test_get_value_edited_configfile():
    """Test 'get_value' function with an edited configuration file."""
    pspp_value = get_value("pspp_path")
    assert pspp_value == "/test/path/test/path"


@pytest.mark.usefixtures("cleanup_config_dict_fx")
def test_get_value_default_values():
    """Test 'get_value' function with default values."""
    pspp_value = get_value("pspp_path")
    schematron_value = get_value("schematron_dirname")
    verapdf_value = get_value("verapdf_path")
    vnu_value = get_value("vnu_path")
    soffice_value = get_value("soffice_path")

    assert pspp_value == "/usr/bin/pspp-convert"
    assert schematron_value == "/usr/share/iso_schematron_xslt1"
    assert verapdf_value == "/usr/share/java/verapdf/verapdf"
    assert vnu_value == "/usr/share/java/vnu/vnu.jar"
    assert soffice_value == "/opt/libreoffice7.2/program/soffice"
