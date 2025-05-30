import json

import pytest
from click.testing import CliRunner
from file_scraper.cmdline import cli
import pathlib

DATA_PATH = pathlib.Path(__file__).parent / "data"


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
    file_path = DATA_PATH / "application_pdf/valid_1.2.pdf"

    runner = CliRunner()
    result = runner.invoke(cli, ["scrape-file", str(file_path)])
    assert result.exit_code == 0
    assert json.loads(result.stdout)["well-formed"] == True


def test_scrape_invalid_file():
    file_path = DATA_PATH / "application_pdf/invalid_1.2_payload_altered.pdf"

    runner = CliRunner()
    result = runner.invoke(cli, ["scrape-file", str(file_path)])
    assert result.exit_code == 0
    assert json.loads(result.stdout)["well-formed"] == False


@pytest.mark.parametrize(
    "flag, output_contains",
    # MimeMatchScraper gives an error when invalid PDF version is provided
    [("--version=1.5", "MimeMatchScraper"),
     ("--tool-info", "tool_info")])
def test_flags_change_output(flag, output_contains):
    """
    Tests that the command gives output based on its flags.
    """

    file_path = DATA_PATH / "application_pdf/valid_A-1a.pdf"
    runner = CliRunner()
    result = runner.invoke(cli, ["scrape-file", str(file_path), flag])
    result_noflag = runner.invoke(cli, ["scrape-file", str(file_path)])
    assert result != result_noflag
    assert result.exit_code == 0
    assert output_contains in result.stdout

    # Check that the output is JSON
    json.loads(result.stdout)


def test_non_existent_file_type():
    file_path = DATA_PATH / "application_pdf/valid_A-1a.pdf"
    runner = CliRunner()
    result = runner.invoke(cli, ["scrape-file", str(file_path),
                                 "--mimetype=non/existent"])
    assert result.exit_code == 1
    assert result.stdout == ("Error: Proper scraper was not found. The file "
                             "was not analyzed.\n")


def test_extra_arguments():
    file_path = DATA_PATH / "text_csv/valid__ascii.csv"
    runner = CliRunner()
    result = runner.invoke(cli, ["scrape-file", str(file_path),
                                 '--fields=["a","b","c"]'])
    assert result.exit_code == 0
    assert ("CSV not well-formed: field counts in the given header "
            "parameter and the CSV header don't match.") in result.stdout


def test_extra_arguments_with_space():
    file_path = DATA_PATH / "text_csv/valid__ascii.csv"
    runner = CliRunner()
    result = runner.invoke(cli, ["scrape-file", str(file_path), '--fields',
                                 '["a","b","c"]'])
    assert result.exit_code == 0
    assert ("CSV not well-formed: field counts in the given header parameter "
            "and the CSV header don't match.") in result.stdout


def test_missing_value_in_extra_argument():
    file_path = DATA_PATH / "text_csv/valid__ascii.csv"
    runner = CliRunner()
    result = runner.invoke(cli, ["scrape-file", str(file_path), '--fields'])
    assert result.exit_code == 1
    assert result.stdout == "Error: No value found for parameter 'fields'\n"


def test_argument_after_argument():
    file_path = DATA_PATH / "text_csv/valid__ascii.csv"
    runner = CliRunner()
    result = runner.invoke(cli, ["scrape-file", str(file_path), '--fields',
                                 '--quotechar="\""'])
    assert result.exit_code == 1
    assert result.stdout == "Error: No value found for parameter 'fields'\n"


def test_incorrect_extra_argument():
    file_path = DATA_PATH / "application_pdf/valid_A-1a.pdf"
    runner = CliRunner()
    result = runner.invoke(cli, ["scrape-file", str(file_path), "abc"])
    assert result.exit_code == 1
    assert result.stdout == ("Error: Unexpected positional "
                             "argument 'abc' encountered\n")


def test_mime_type_cases():
    file_path = DATA_PATH / "application_pdf/valid_1.2.pdf"

    runner = CliRunner()
    result = runner.invoke(cli, ["scrape-file", "--mimetype", "Application/pdf", str(file_path)])
    assert result.exit_code == 0
    assert json.loads(result.stdout)["well-formed"] == True
