"""
Command line interface for file-scraper
"""

from __future__ import print_function

import click
#import json

#from file_scraper.scraper import Scraper


@click.group()
def cli():
    pass


@cli.command()
@click.argument("filename", type=click.Path(exists=True))
def scrape_file(filename):
    """
    todo
    """  # TODO
    print(filename)


if __name__ == "__main__":
    cli()
