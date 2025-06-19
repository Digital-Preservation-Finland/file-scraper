"""Tests for config.py."""
import pytest

from file_scraper.paths import resolve_command, resolve_path_from_config


@pytest.fixture(scope="function")
def config_file_fx(monkeypatch):
    """
    Set the environment variable 'FILE_SCRAPER_CONFIG' to a test configuration
    file.
    """
    monkeypatch.setenv("FILE_SCRAPER_CONFIG", "tests/config/test.conf")


@pytest.mark.usefixtures("config_file_fx")
def test_resolve_command_with_edited_configfile():
    """
    Test 'resolve_command' function with an edited configuration file. If the
    command is not in the configuration file resolve the command from $PATH
    otherwise raises an error which is tested elsewhere
    """
    pspp_exec = resolve_command("pspp-convert")
    assert pspp_exec == "/test/path/test/pspp-convert"

    # Executable which is not in the configuration file still found from $PATH
    cd_exec = resolve_command("cd")
    assert cd_exec in ["/usr/bin/cd", "/bin/cd"]


@pytest.mark.usefixtures("config_file_fx")
def test_resolve_path_from_config_with_edited_configfile():
    """
    Test 'resolve_path_from_config' will only attempt to find the value from
    the configuration file otherwise raises an error which is tested elsewhere.
    """
    schematron_value = resolve_path_from_config("schematron_dir")
    assert schematron_value == "/usr/share/iso_schematron_xslt1/"


@pytest.mark.parametrize("info, path", [
    ("schematron_dir", "/usr/share/iso_schematron_xslt1/"),
    ("magiclib", "/opt/file-5.45/lib64/libmagic.so.1")])
def test_resolve_path_from_config(info, path):
    value = resolve_path_from_config(info)
    assert value == path


def test_invalid_config_and_command_parameter():
    """
    Test that function resolve_command raises a NameError when values cannot
    be found from the configuration file or path.
    Also test resolve_path_from_config which searches only configuration file
    """
    with pytest.raises(NameError):
        resolve_command("nowaythisconfigactuallyexists")
    with pytest.raises(NameError):
        resolve_path_from_config("nowaythisconfiactuallyexists")
