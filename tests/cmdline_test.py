import json

import pytest
from click.testing import CliRunner
from file_scraper.cmdline import cli
import pathlib

DATA_PATH = pathlib.Path(__file__).parent / "data"


def get_cli_runner(*args, **kwargs):
    """
    Return CliRunner with separate stdout and stderr. Click 8.1 and older
    requires a `mix_stderr=False` which has been removed in newer Click
    """
    try:
        # Click 8.1 and older
        return CliRunner(*args, **kwargs, mix_stderr=False)
    except TypeError:
        # Click 8.2 and newer
        return CliRunner(*args, **kwargs)


def test_group_command_lists_commands():
    runner = get_cli_runner()
    result = runner.invoke(cli, [])
    assert "scrape-file" in result.stdout
    assert result.exit_code == 0


def test_scraper_without_arguments():
    runner = get_cli_runner()
    result = runner.invoke(cli, ["scrape-file"])
    assert "Error: Missing argument 'FILENAME'" in result.stderr
    assert result.exit_code == 2


def test_scrape_valid_file():
    file_path = DATA_PATH / "application_pdf/valid_1.2.pdf"

    runner = get_cli_runner()
    result = runner.invoke(cli, ["scrape-file", str(file_path)])
    data = json.loads(result.stdout)
    assert data["well-formed"] is True
    assert data["path"] == str(file_path)
    assert result.exit_code == 0


def test_scrape_invalid_file():
    file_path = DATA_PATH / "application_pdf/invalid_1.2_payload_altered.pdf"

    runner = get_cli_runner()
    result = runner.invoke(cli, ["scrape-file", str(file_path)])
    assert json.loads(result.stdout)["well-formed"] is False
    assert result.exit_code == 0


@pytest.mark.parametrize(
    "message, input",
    [
        ("Instead of a file, a directory was found from the path: ", "dir"),
        ("A file couldn't be found from the path: ", "nonSenseFiLe"),
        ("The file is not a regular file and can't be scraped "
         + "from the path:", "/dev/null")
    ]
)
def test_scraper_invalid_paths(tmp_path_factory, message: str, input: str):
    """
    Invalid paths are not
    """

    if input == "dir":
        input = str(tmp_path_factory.mktemp("test"))
    runner = get_cli_runner()
    result = runner.invoke(cli, ["scrape-file", input])
    assert message in result.stderr
    assert result.exit_code in [1, 2]


# Much slower than testing using only the scraper class, but also tests the
# cli reaction to the incorrect parameters.
@pytest.mark.parametrize(
    "flags, error_message",
    [(["--version=1.5"],
      "Missing a mimetype parameter for the provided version 1.5"),
     (["--mimetype=application/pdf", "--version=(:unav)"],
      "Given version (:unav) for the mimetype application/pdf"
      " is not supported"),
     (["--mimetype=(:unav)"],
      "Given mimetype (:unav) is not supported"),
     (["--mimetype=application/not_supported"],
      "Given mimetype application/not_supported is not supported"),
     (["--mimetype=application/pdf", "--version=9.99"],
      "Given version 9.99 for the mimetype application/pdf is not supported"),
     ]
)
def test_incorrect_flags(flags: list[str], error_message: str):
    """
    Tests that scraper doesn't allow weird combination of flags
    """

    file_path = DATA_PATH / "application_pdf/valid_A-1a.pdf"
    runner = get_cli_runner()
    result = runner.invoke(cli, ["scrape-file", str(file_path), *flags])
    assert error_message in result.stderr
    assert "Unknown error" not in result.stderr
    assert result.exit_code == 2


# TODO add mimetype and version combination flags when handled.
@pytest.mark.parametrize(
    "flag, output_contains",
    [
        (["--mimetype=application/pdf", "--version=A-2u"],
            "Predefined version \'A-2u\' and resulted version \'A-1a\' "
            "mismatch."),
        (["--tool-info"], "tool_info")
    ]
    )
def test_flags(flag, output_contains):
    """
    Tests that the command gives output based on its flags.
    """

    file_path = DATA_PATH / "application_pdf/valid_A-1a.pdf"
    runner = get_cli_runner()
    result = runner.invoke(cli, ["scrape-file", str(file_path), *flag])
    result_noflag = runner.invoke(cli, ["scrape-file", str(file_path)])
    assert result != result_noflag
    assert output_contains in result.stdout
    assert result.exit_code == 0

    # Check that the output is JSON
    json.loads(result.stdout)


def test_extra_arguments():
    file_path = DATA_PATH / "text_csv/valid__ascii.csv"
    runner = get_cli_runner()
    result = runner.invoke(cli, ["scrape-file", str(file_path),
                                 '--fields=["a","b","c"]'])
    assert ("CSV not well-formed: field counts in the given header "
            "parameter and the CSV header don't match.") in result.stdout
    assert result.exit_code == 0


def test_extra_arguments_with_space():
    file_path = DATA_PATH / "text_csv/valid__ascii.csv"
    runner = get_cli_runner()
    result = runner.invoke(cli, ["scrape-file", str(file_path), '--fields',
                                 '["a","b","c"]'])
    assert ("CSV not well-formed: field counts in the given header parameter "
            "and the CSV header don't match.") in result.stdout
    assert result.exit_code == 0


def test_missing_value_in_extra_argument():
    file_path = DATA_PATH / "text_csv/valid__ascii.csv"
    runner = get_cli_runner()
    result = runner.invoke(cli, ["scrape-file", "--fields", str(file_path)])
    assert "Error: Missing argument 'FILENAME'." in result.stderr
    assert result.exit_code == 2


def test_argument_after_argument():
    """
    Test that an reasonable exception gets raised when the --fields option
    is missing an argument.
    """
    file_path = DATA_PATH / "text_csv/valid__ascii.csv"
    runner = get_cli_runner()
    result = runner.invoke(
        cli, ["scrape-file", '--fields', '--quotechar', '"', str(file_path)])
    # the command parser affects the accuracy of the error message.
    assert "Error: Got unexpected extra argument" in result.stderr
    assert result.exit_code == 2


def test_incorrect_extra_argument():
    file_path = DATA_PATH / "application_pdf/valid_A-1a.pdf"
    runner = get_cli_runner()
    result = runner.invoke(cli, ["scrape-file", "--abc", str(file_path)])
    assert "Error: No such option: --abc" in result.stderr
    assert result.exit_code == 2


def test_mime_type_cases():
    file_path = DATA_PATH / "application_pdf/valid_1.2.pdf"

    runner = get_cli_runner()
    result = runner.invoke(
        cli, ["scrape-file", "--mimetype", "Application/pdf", str(file_path)])
    assert json.loads(result.stdout)["well-formed"] is True
    assert result.exit_code == 0


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

    runner = get_cli_runner()

    result = runner.invoke(cli, ["scrape-file", flag, str(file_path)])

    assert expected_output in result.stderr


def test_valid_schematron_command():
    runner = get_cli_runner()
    result = runner.invoke(
            cli,
            [
                "check-xml-schematron-features",
                "--schematron",
                "tests/data/text_xml/supplementary/local.sch",
                "tests/data/text_xml/valid_1.0_well_formed.xml"
            ]
        )
    result_json = json.loads(result.stdout)
    assert result_json["well-formed"] is True
    assert result_json["MIME type"] == "text/xml"
    assert result_json["version"] == "1.0"


def test_invalid_schematron_command():
    runner = get_cli_runner()
    result = runner.invoke(
            cli,
            [
                "check-xml-schematron-features",
                "--schematron",
                "tests/data/text_xml/supplementary/local.sch",
                "tests/data/text_xml/invalid_1.0_local_xsd.xml"
            ]
        )
    result_json = json.loads(result.stdout)
    assert result_json["well-formed"] is False


def test_sgml_catalog_files_env_var_gets_overridden():
    runner = get_cli_runner(
        env={"SGML_CATALOG_FILES": "/some/invalid/catalog"})
    result = runner.invoke(cli, ["scrape-file",
                                 "tests/data/text_xml/valid_1.0_gpx_1.0.xml"])
    assert json.loads(result.stdout)["well-formed"] is True
    assert result.exit_code == 0

    runner = get_cli_runner()
    result = runner.invoke(cli, ["scrape-file",
                                 "--catalog-path", "/some/invalid/catalog",
                                 "tests/data/text_xml/valid_1.0_gpx_1.0.xml"])
    assert json.loads(result.stdout)["well-formed"] is False
    assert result.exit_code == 0
