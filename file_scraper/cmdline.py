"""
Command line interface for file-scraper
"""


import json
import logging

import click

from file_scraper.logger import LOGGER, enable_logging
from file_scraper.scraper import Scraper
from file_scraper.utils import ensure_text


@click.group()
def cli():
    """Scrape files"""


# pylint: disable=too-many-arguments
@cli.command("scrape-file", context_settings={'ignore_unknown_options': True,
                                              'allow_extra_args': True})
@click.argument("filename", type=click.Path(exists=True))
@click.argument("scraper_args", nargs=-1, type=click.UNPROCESSED)
@click.option("--skip-wellformed-check", "check_wellformed",
              default=True, flag_value=False,
              help="Don't check the file well-formedness, only scrape "
                   "metadata")
@click.option("--tool-info", default=False, is_flag=True,
              help="Include errors and messages from different 3rd party "
                   "tools that were used")
@click.option("--mimetype", default=None,
              help="Specify the mimetype of the file")
@click.option("--version", default=None,
              help="Specify version for the filetype")
@click.option(
    "--verbose", "-v", count=True,
    help=(
        "Print detailed information about execution. "
        "Can be provided twice for additional verbosity."
    )
)
@click.pass_context
def scrape_file(
        ctx, filename, scraper_args, check_wellformed, tool_info, mimetype,
        version, verbose):
    """
    Identify file type, collect metadata, and optionally check well-formedness.

    In addition to the given options, the user can provide any extra options
    after FILENAME that are passed onto the scraper. These options must be
    in the long form, e.g. "--charset=UTF-8" or "--charset UTF-8".
    \f

    :ctx: Context object
    :filename: Path to the file that should be scraped
    :check_wellformed: Flag whether the scraper checks wellformedness
    :tool_info: Flag whether the scraper includes messages from different 3rd
                party tools
    :mimetype: Specified mimetype for the scraped file
    :version: Specified version for the scraped file
    """
    level = {
        0: logging.WARNING,
        1: logging.INFO,
        2: logging.DEBUG
    }

    # Enable logging. If flag is provided an additional number of times,
    # default to the highest possible verbosity.
    enable_logging(level.get(verbose, logging.DEBUG))

    LOGGER.info("Additional scraper args provided: %s", scraper_args)

    scraper = Scraper(filename, mimetype=mimetype, version=version,
                      **_extra_options_to_dict(scraper_args))
    scraper.scrape(check_wellformed=check_wellformed)

    results = {
        "path": str(scraper.path),
        "MIME type": ensure_text(scraper.mimetype),
        "version": ensure_text(scraper.version),
        "metadata": scraper.streams,
        "grade": scraper.grade()
    }
    if check_wellformed:
        results["well-formed"] = scraper.well_formed
    if tool_info:
        results["tool_info"] = scraper.info

    errors = {}

    for item in scraper.info.values():
        if "ScraperNotFound" in item["class"]:
            raise click.ClickException("Proper scraper was not found. The "
                                       "file was not analyzed.")

        if item["errors"]:
            errors[item["class"]] = item["errors"]

    if errors:
        results["errors"] = errors

    click.echo(json.dumps(results, indent=4))


def _extra_options_to_dict(args):
    """
    Create a dict from the extra options and return it.

    If string representations of boolean values (e.g. "True") are encountered,
    their boolean counterparts are used.

    These extra parameters are expected to be in format `--key=value` or
    `--key value`. Missing values or encountered positional arguments raise a
    ClickException with an explanatory message to be printed to the user by
    click.

    :args: A list of arguments that were not handled by click.
    :returns: A dictionary containing option names (as dictionary keys) and
              their values.
    """
    option_dict = {}
    next_option_index = 0
    while next_option_index < len(args):
        current_option = args[next_option_index]

        if current_option.find("--") != 0:
            raise click.ClickException(
                f"Unexpected positional argument "
                f"'{current_option}' encountered")
        current_option = current_option.lstrip("--")

        if "=" in current_option:  # --key=value
            [key, value] = current_option.split("=", 1)
            next_option_index += 1
        else:  # --key value
            key = current_option

            try:
                value = args[next_option_index + 1]
            except IndexError:
                # ClickException is a special type of exception that signals to
                # the user that not everything went well. No need for the
                # enhanced stack trace there.
                # pylint: disable=raise-missing-from
                raise click.ClickException(
                    f"No value found for parameter '{key}'")

            if value[0] == "-":
                raise click.ClickException(
                    f"No value found for parameter '{key}'")
            next_option_index += 2
        option_dict[key] = _string_to_bool(value)

    return option_dict


def _string_to_bool(element):
    if element.lower() == "true":
        element = True
    elif element.lower() == "false":
        element = False

    return element


if __name__ == "__main__":
    cli()
