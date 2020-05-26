"""
Command line interface for file-scraper
"""

from __future__ import print_function

import click
import json

from file_scraper.scraper import Scraper


@click.group()
def cli():
    pass


@cli.command()
@click.argument("filename", type=click.Path(exists=True))
@click.option("--no-wellformedness", "check_wellformed",
              default=True, flag_value=False,
              help="Don't check if the file is well-formed, only scrape "
                   "metadata")
@click.option("--tool-info", default=False, is_flag=True,
              help="Include errors and messages from different 3rd party "
                   "tools that were used")
def scrape_file(filename, check_wellformed, tool_info):
    """
    Identify file type, collect metadata, and optionally check well-formedness.

    TODO describe more
    """  # TODO
    scraper = Scraper(filename, check_wellformed=check_wellformed)
    scraper.scrape()

    results = {
        "path": scraper.filename,
        "MIME type": scraper.mimetype,
        "version": scraper.version,
        "metadata": scraper.streams,
        }
    if check_wellformed:
        results["well-formed"] = scraper.well_formed
    if tool_info:
        results["tool_info"] = scraper.info

    click.echo(json.dumps(results, indent=4))


if __name__ == "__main__":
    cli()
