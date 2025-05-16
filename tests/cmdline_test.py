import pytest
from click.testing import CliRunner
from file_scraper.cmdline import cli
import pathlib

data_path = pathlib.Path(__file__).parent / "data"


def _get_cmdline_options():
    return ["--skip-wellformed-check", "--tool-info",
            "--version", "--mimetype"]


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


@pytest.mark.parametrize(
    "filename, flag, output",
    [(data_path / "application_pdf/valid_A-1a.pdf", "--version=1.5", ""),
     (data_path / "application_pdf/valid_A-1a.pdf", "--tool-info", "")])
def test_flags_change_output(filename, flag, output):
    """"""

    runner = CliRunner()
    result = runner.invoke(cli, ["scrape-file", str(filename), flag])
    result_noflag = runner.invoke(cli, ["scrape-file", filename])
    assert result != result_noflag
    assert result.exit_code == 0
