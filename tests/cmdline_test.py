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

    data = json.loads(result.stdout)
    assert data["well-formed"] is True
    assert data["path"] == str(file_path)


def test_scrape_invalid_file():
    file_path = DATA_PATH / "application_pdf/invalid_1.2_payload_altered.pdf"

    runner = CliRunner()
    result = runner.invoke(cli, ["scrape-file", str(file_path)])
    assert result.exit_code == 0
    assert json.loads(result.stdout)["well-formed"] == False


@pytest.mark.parametrize(
    "flag, output_contains",
    # MimeMatchExtractor gives an error when invalid PDF version is provided
    [("--version=1.5", "MimeMatchExtractor"),
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
    assert result.stdout == ("Error: Proper extractor was not found. The file "
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
    result = runner.invoke(cli, ["scrape-file", "--fields", str(file_path)])
    assert result.exit_code == 2
    assert "Error: Missing argument 'FILENAME'." in result.stdout


def test_argument_after_argument():
    file_path = DATA_PATH / "text_csv/valid__ascii.csv"
    runner = CliRunner()
    result = runner.invoke(cli, ["scrape-file", '--fields', '--quotechar', '"',
                                 str(file_path)])
    assert result.exit_code == 2
    assert "Invalid value for 'FILENAME': Path '\"' does not exist." in result.stdout


def test_incorrect_extra_argument():
    file_path = DATA_PATH / "application_pdf/valid_A-1a.pdf"
    runner = CliRunner()
    result = runner.invoke(cli, ["scrape-file", "--abc", str(file_path)])
    assert result.exit_code == 2
    assert "Error: No such option: --abc" in result.stdout


def test_mime_type_cases():
    file_path = DATA_PATH / "application_pdf/valid_1.2.pdf"

    runner = CliRunner()
    result = runner.invoke(cli,
                           ["scrape-file", "--mimetype", "Application/pdf",
                            str(file_path)])
    assert result.exit_code == 0
    assert json.loads(result.stdout)["well-formed"] == True


@pytest.mark.parametrize(
    "flag,expected_output",
    [
        ("-v", "INFO"),
        ("-vv", "DEBUG")
    ]
)
def test_verbose_flag(flag, expected_output, caplog):
    """
    Test that `-v` and `-vv` cause INFO and DEBUG log messages to be printed
    respectively
    """
    file_path = DATA_PATH / "application_pdf/valid_A-1a.pdf"

    try:
        runner = CliRunner(mix_stderr=False)
    except TypeError:  # 'mix_stderr' removed in Click 8.2+
        runner = CliRunner()

    result = runner.invoke(cli, ["scrape-file", flag, str(file_path)])

    assert expected_output in result.stderr


def test_valid_schematron_command():
    runner = CliRunner()
    result = runner.invoke(cli, ["check-xml-schematron-features",
                                 "--schematron",
                                 "tests/data/text_xml/supplementary/local.sch",
                                 "tests/data/text_xml/valid_1.0_well_formed.xml"])
    result_json = json.loads(result.stdout)
    assert result_json["well-formed"] == True
    assert result_json["MIME type"] == "text/xml"
    assert result_json["version"] == "1.0"

def test_invalid_schematron_command():
    runner = CliRunner()
    result = runner.invoke(cli, ["check-xml-schematron-features",
                                 "--schematron",
                                 "tests/data/text_xml/supplementary/local.sch",
                                 "tests/data/text_xml/invalid_1.0_local_xsd.xml"])
    result_json = json.loads(result.stdout)
    assert result_json["well-formed"] == False
