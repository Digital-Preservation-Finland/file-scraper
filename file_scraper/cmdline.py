"""
Command line interface for file-scraper
"""

import json
import logging

import click

from file_scraper.logger import LOGGER, enable_logging
from file_scraper.schematron.schematron_model import SchematronMeta
from file_scraper.schematron.schematron_scraper import SchematronScraper
from file_scraper.scraper import Scraper
from file_scraper.utils import ensure_text


@click.group()
def cli():
    """Scrape files"""


# pylint: disable=too-many-arguments
@cli.command("scrape-file")
@click.argument("filename", type=click.Path(exists=True))
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
@click.option("--charset", help="Specify the encoding used in text files.")
@click.option("--delimiter",
              help="Specify the delimiter in CSV files.")
@click.option("--fields", help="Specify the headers in CSV files.")
@click.option("--separator",
              help="Specify the separator (line terminator) in CSV files.")
@click.option("--quotechar", help="Specify the quote character in CSV files.")
@click.option("--schema", help="Specify the schema file for XML files.")
@click.option("--catalogs", help="Use local catalog schemas for XML files.")
@click.option("--no_network", type=click.BOOL,
              help="Disallow network usage for XML files.")
@click.option("--catalog_path",
              help="Specify the catalog environment for XML files.")
def scrape_file(
        filename, check_wellformed, tool_info, mimetype, version, verbose,
        charset, delimiter, fields, separator, quotechar, schema, catalogs,
        no_network, catalog_path):
    """
    Identify file type, collect metadata, and optionally check well-formedness.
    \f

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

    option_args = {"charset": charset, "delimiter": delimiter,
                   "fields": fields,
                   "separator": separator, "quotechar": quotechar,
                   "schema": schema, "catalogs": catalogs,
                   "no_network": no_network, "catalog_path": catalog_path}

    # Enable logging. If flag is provided an additional number of times,
    # default to the highest possible verbosity.
    enable_logging(level.get(verbose, logging.DEBUG))

    LOGGER.info("Additional scraper args provided: %s", option_args)
    scraper = Scraper(filename, mimetype=mimetype, version=version,
                      **option_args)
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


@cli.command("check-xml-schematron-features")
@click.argument("filename", type=click.Path(exists=True))
@click.option("--no-network", type=click.BOOL,
              help="Disallow network usage for XML files.")
@click.option("--schema", help="Specify the schema file for XML files.")
@click.option("--schematron",
              help="Specify the schematron file for XML schematron checks.")
@click.option("--schematron-verbose", type=click.BOOL,
              help="Specify the verboseness for XML schematron checks")
@click.option("--cache", type=click.BOOL,
              help="Specify caching for XML schematron checks.")
@click.option("--catalog-path",
              help="Specify the catalog environment for XML files.")
@click.option("--catalogs", help="Use local catalog schemas for XML files.")
@click.option("--extra-hash",
              help="Hash of related abstract patterns for XML schematron "
                   "checks.")
@click.option(
    "--verbose", "-v", count=True,
    help=(
            "Print detailed information about execution. "
            "Can be provided twice for additional verbosity."
    )
)
def check_xml_schematron_features(filename, no_network, schema, schematron,
                                  schematron_verbose, cache, catalog_path,
                                  catalogs, extra_hash, verbose):
    option_args = {"no_network": no_network, "schema": schema,
                   "schematron": schematron, "verbose": schematron_verbose,
                   "cache": cache, "catalog_path": catalog_path,
                   "catalogs": catalogs, "extra_hash": extra_hash}

    level = {
        0: logging.WARNING,
        1: logging.INFO,
        2: logging.DEBUG
    }

    # Enable logging. If flag is provided an additional number of times,
    # default to the highest possible verbosity.
    enable_logging(level.get(verbose, logging.DEBUG))

    LOGGER.info("Additional scraper args provided: %s", option_args)

    schematron_scraper = SchematronScraper(filename, "text/xml",
                                           params=option_args)
    schematron_scraper.scrape_file()

    schematron_meta = schematron_scraper.streams[0]
    metadata = {}
    for method in schematron_meta.iterate_metadata_methods():
        metadata[method.__name__] = method()

    results = {
        "path": str(schematron_scraper.filename),
        "MIME type": ensure_text(schematron_meta.mimetype()),
        "version": ensure_text(schematron_meta.version()),
        "metadata": metadata,
        "well-formed": schematron_scraper.well_formed
    }

    errors = {}

    if schematron_scraper.info()["errors"]:
        errors[schematron_scraper.info()["class"]] = schematron_scraper.info()[
            "errors"]

    if errors:
        results["errors"] = errors

    click.echo(json.dumps(results, indent=4))


if __name__ == "__main__":
    cli()
