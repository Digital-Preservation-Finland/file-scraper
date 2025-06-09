"""Tests for config.py."""
import pytest

from file_scraper.paths import resolve_path, SOFTWARE_LOCATIONS as S_L


@pytest.fixture(scope="function")
def config_file_fx(monkeypatch):
    """
    Set the environment variable 'FILE_SCRAPER_CONFIG' to a test configuration
    file."""
    monkeypatch.setenv("FILE_SCRAPER_CONFIG", "tests/config/test.conf")
    monkeypatch.setitem(S_L["PSPP"],
                        "config_name", "pspp_path")


@pytest.mark.usefixtures("config_file_fx")
def test_get_value_edited_configfile():
    """Test 'get_value' function with an edited configuration file. If a new
    value is set in the configuration file, 'get_value' returns it. Otherwise
    it returns the default value.
    """
    pspp_value = resolve_path(S_L["PSPP"])
    assert pspp_value == "/test/path/test/path"

    schematron_value = resolve_path(S_L["SCHEMATRON_DIR"])
    assert schematron_value == "/usr/share/iso_schematron_xslt1/"


@pytest.mark.parametrize("info, path", [
    (S_L["PSPP"], "/usr/bin/pspp-convert"),
    (S_L["SCHEMATRON_DIR"], "/usr/share/iso_schematron_xslt1/"),
    (S_L["VERAPDF"], "/usr/bin/verapdf"),
    (S_L["VNU"], "/usr/bin/vnu"),
    (S_L["SOFFICE"], "/opt/libreoffice24.8/program/soffice"),
    (S_L["GHOSTSCRIPT"], "/opt/ghostscript-10.03/bin/gs")])
def test_get_value_default_values(info, path):
    """Test resolve_path function with some values."""
    value = resolve_path(info)
    assert value == path


def test_invalid_config_and_command_parameter():
    """
    Test that values which are not included in the config file or
    cannot be resolved from path raise a NameError.
    """
    with pytest.raises(NameError):
        resolve_path({"config_name": "nowaythisconfigactuallyexists",
                      "command": None})
