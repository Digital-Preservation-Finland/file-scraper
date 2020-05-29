"""
Command line interface for file-scraper
"""

from __future__ import print_function

import json
import click

from file_scraper.scraper import Scraper


@click.group()
def cli():
    pass


@cli.command("scrape-file", context_settings=dict(
    ignore_unknown_options=True,
    allow_extra_args=True,
))
@click.argument("filename", type=click.Path(exists=True))
@click.option("--no-wellformedness", "check_wellformed",
              default=True, flag_value=False,
              help="Don't check if the file is well-formed, only scrape "
                   "metadata")
@click.option("--tool-info", default=False, is_flag=True,
              help="Include errors and messages from different 3rd party "
                   "tools that were used")
@click.option("--mimetype", default=None,
              help="Specify the mimetype of the file")
@click.option("--version", default=None,
              help="Specify version for the filetype")
@click.pass_context
def scrape_file(ctx, filename, check_wellformed, tool_info, mimetype, version):
    """
    Identify file type, collect metadata, and optionally check well-formedness.

    In addition to the given options, the user can provide any extra arguments
    that are passed onto the scraper. The arguments must be in the form
    ``key=value``. Only string and boolean values are possible.
    TODO describe more
    """  # TODO
    # Turn the list of extra arguments into a dict that can be passed to
    # the scraper, and append the explicit click options to that
    params_split = [element for item in ctx.args for element in item.split("=")]
    params_split = [_string_to_bool(element) for element in params_split]
    params_dict = dict(zip(params_split[::2], params_split[1::2]))
    params_dict.update(check_wellformed=check_wellformed,
                       mimetype=mimetype, version=version)

    scraper = Scraper(filename, **params_dict)
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


def _string_to_bool(element):
    if element.lower() == "true":
        element = True
    elif element.lower() == "false":
        element = False

    return element


if __name__ == "__main__":
    cli()
