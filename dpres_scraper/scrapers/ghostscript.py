"""
This is a PDF scraper implemented with ghostscript.
"""

from dpres_scraper.base import BaseScraper, Shell


class GhostScript(BaseScraper):
    """
    Ghostscript pdf scraper
    """
    _supported = {'application/pdf': ['1.7', 'A-1a', 'A-1b', 'A-2a', 'A-2b',
                                      'A-2u', 'A-3a', 'A-3b', 'A-3u']}
    _only_wellformed = True

    def scrape_file(self):
        """
        Scrape file
        """

        shell = Shell([
            'gs', '-o', '/dev/null', '-sDEVICE=nullpage',
            self.filename])

        # Ghostscript will result 0 if it can repair errors.
        # However, stderr is not then empty.
        # This case should be handled as validation failure.
        if shell.stderr:
            self.errors(shell.stderr.decode('iso-8859-1').encode('utf8'))
        elif shell.returncode != 0:
            self.errors("Ghostscript returned return code: %s"
                        % shell.returncode)
        self.messages(shell.stdout.decode('iso-8859-1').encode('utf8'))
        self._collect_elements()

    # pylint: disable=no-self-use
    def _s_stream_type(self):
        """Return file type
        """
        return 'binary'
