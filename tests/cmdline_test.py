import json

import pytest
from click.testing import CliRunner
from file_scraper.cmdline import cli
import pathlib

data_path = pathlib.Path(__file__).parent / "data"


def test_group_command_lists_commands():
    runner = CliRunner()
    result = runner.invoke(cli, [])
    assert result.exit_code == 0
    assert "scrape-file" in result.output


def test_scraper_without_arguments():
    runner = CliRunner()
    result = runner.invoke(cli, ["scrape-file"])
    assert result.exit_code == 2
    assert "Error: Missing argument 'FILENAME'" in result.output


def test_scrape_valid_file():
    file_path = data_path / "application_pdf/valid_1.2.pdf"

    runner = CliRunner()
    result = runner.invoke(cli, ["scrape-file", str(file_path)])
    assert result.exit_code == 0
    assert '"well-formed": true' in result.stdout

def test_scrape_invalid_file():
    file_path = data_path / "application_pdf/invalid_1.2_payload_altered.pdf"

    runner = CliRunner()
    result = runner.invoke(cli, ["scrape-file", str(file_path)])
    assert result.exit_code == 0
    assert '"well-formed": false' in result.stdout




@pytest.mark.parametrize(
    "filename, flag, output",
    [("application_pdf/valid_A-1a.pdf", "--version=1.5", ""),
     ("application_pdf/valid_A-1a.pdf", "--tool-info", "")])
def test_flags_change_output(filename, flag, output):
    """"""

    file_path = data_path / filename
    runner = CliRunner()
    result = runner.invoke(cli, ["scrape-file", str(file_path), flag])
    result_noflag = runner.invoke(cli, ["scrape-file", str(file_path)])
    assert result != result_noflag
    assert result.exit_code == 0
