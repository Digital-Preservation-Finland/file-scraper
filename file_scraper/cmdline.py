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
def scrape_file(filename):
    """
    Identify file type, collect metadata, and optionally check well-formedness.

    TODO describe more
    """  # TODO
    scraper = Scraper(filename)
    scraper.scrape()
    results = {
        "path": scraper.filename,
        "MIME type": scraper.mimetype,
        "version": scraper.version,
        "metadata": scraper.streams,
        }
    # TODO well-formedness info if available
    # TODO info
    print(json.dumps(results, indent=4))


if __name__ == "__main__":
    cli()
