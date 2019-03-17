"""
This is a Schematron scraper.
"""
import os
import shutil
import tempfile
import lxml.etree as etree
from file_scraper.utils import hexdigest
from file_scraper.base import BaseScraper, Shell


class Schematron(BaseScraper):
    """Schematron scraper
    """
    _supported = {'text/xml': ['1.0']}  # Supported mimetypes
    _only_wellformed = True

    def __init__(self, filename, mimetype, validation=True, params=None):
        """Initialize instance.
        :filename: File path
        :mimetype: Predicted mimetype of the file
        :validation: True for the full validation, False for just
                     identification and metadata scraping
        :params: Extra parameters needed for the scraper
        """
        self._verbose = params.get('verbose', False)
        self._cache = params.get('cache', True)
        self._cachepath = os.path.expanduser(
            '~/.file-scraper/schematron-cache')
        self._schematron_dirname = params.get('compile_path', None)
        self._returncode = None
        self._schematron_file = params.get('schematron', None)
        self._extra_hash = params.get('extra_hash', None)
        super(Schematron, self).__init__(filename, mimetype,
                                         validation, params)

    @classmethod
    def is_supported(cls, mimetype, version=None,
                     validation=True, params=None):
        """We use this scraper only with a schematron file
        :mimetype: Identified mimetype
        :version: Identified version (if needed)
        :validation: True for the full validation, False for just
                     identification and metadata scraping
        :params: Extra parameters needed for the scraper
        :returns: True if scraper is supported
        """
        if params is None:
            params = {}
        if 'schematron' not in params:
            return False
        return super(Schematron, cls).is_supported(
            mimetype, version, validation, params)

    @property
    def well_formed(self):
        """Check if document resulted errors.
        """
        if len(self.errors()) == 0 and len(self.messages()) > 0:
            if self.messages().find('<svrl:failed-assert ') < 0 \
                    and self._returncode == 0:
                return True
        return False

    def scrape_file(self):
        """Do the Schematron validation.
        """
        if self._schematron_file is None:
            return

        xslt_filename = self._compile_schematron(self._schematron_file)

        # The actual validation
        shell = self._compile_phase(
            stylesheet=xslt_filename,
            inputfile=self.filename, valid_codes=[0, 6])

        self._returncode = shell.returncode
        self.errors(shell.stderr)

        if not self._verbose and shell.returncode == 0:
            self.messages(self._filter_duplicate_elements(shell.stdout))
        else:
            self.messages(shell.stdout)
        self._check_supported()
        self._collect_elements()

    # pylint: disable=no-self-use
    def _s_stream_type(self):
        """Return file type
        """
        return 'text'

    def _filter_duplicate_elements(self, result):
        """Filter duplicate elements from the result
        :result: Result as string
        """
        SVRL = {'svrl': 'http://purl.oclc.org/dsdl/svrl'}
        root = etree.fromstring(result)
        patterns = root.xpath('./svrl:active-pattern', namespaces=SVRL)
        for pattern in patterns:
            prev = pattern.xpath('preceding-sibling::svrl:active-pattern[1]',
                                 namespaces=SVRL)
            if prev and pattern.get('id') == prev[0].get('id'):
                pattern.getparent().remove(pattern)

        rules = root.xpath('svrl:fired-rule', namespaces=SVRL)
        for rule in rules:
            prev = rule.xpath('preceding-sibling::svrl:fired-rule[1]',
                              namespaces=SVRL)
            if prev and rule.get('context') == prev[0].get('context'):
                rule.getparent().remove(rule)

        return etree.tostring(
            root, pretty_print=True, xml_declaration=False,
            encoding='UTF-8', with_comments=True)

    def _compile_phase(self, stylesheet, inputfile, valid_codes,
                       outputfile=None, outputfilter=False):
        """Compile one phase
        :stylesheet: XSLT file to used in the conversion
        :inputfile: Input document filename
        :outputfile: Filename of the resulted document, stdout if None
        :outputfilter: Use outputfilter parameter with value only_messages
        :return: Shell instance
        """
        cmd = ['xsltproc']
        if outputfile:
            cmd = cmd + ['-o', outputfile]
        if outputfilter and not self._verbose:
            cmd = cmd + ['--stringparam', 'outputfilter', 'only_messages']
        cmd = cmd + [os.path.join(self._schematron_dirname, stylesheet),
                     inputfile]
        shell = Shell(cmd)
        if shell.returncode not in valid_codes:
            raise SchematronValidatorError(
                "Error %s\nstdout:\n%s\nstderr:\n%s" % (
                    shell.returncode, shell.stdout, shell.stderr))
        return shell

    def _compile_schematron(self, schematron_file):
        """Compile a schematron file
        :schematron_file: Schematron file name
        :returns: XSLT file name
        """
        xslt_filename = self._generate_xslt_filename(schematron_file)
        tempdir = tempfile.mkdtemp()

        if self._cache:
            if os.path.isfile(xslt_filename):
                return xslt_filename

        try:
            self._compile_phase(
                stylesheet='iso_dsdl_include.xsl',
                inputfile=schematron_file,
                outputfile=os.path.join(tempdir, 'step1.xsl'),
                valid_codes=[0])
            self._compile_phase(
                stylesheet='iso_abstract_expand.xsl',
                inputfile=os.path.join(tempdir, 'step1.xsl'),
                outputfile=os.path.join(tempdir, 'step2.xsl'),
                valid_codes=[0])
            self._compile_phase(
                stylesheet='optimize_schematron.xsl',
                inputfile=os.path.join(tempdir, 'step2.xsl'),
                outputfile=os.path.join(tempdir, 'step3.xsl'),
                valid_codes=[0])
            self._compile_phase(
                stylesheet='iso_svrl_for_xslt1.xsl',
                inputfile=os.path.join(tempdir, 'step3.xsl'),
                outputfile=os.path.join(tempdir, 'validator.xsl'),
                outputfilter=not(self._verbose),
                valid_codes=[0])

            shutil.move(os.path.join(tempdir, 'validator.xsl'),
                        xslt_filename)

        finally:
            shutil.rmtree(tempdir)

        return xslt_filename

    def _generate_xslt_filename(self, schematron_schema):
        """Generate XSLT filename from schematron file
        :schematron_schema: Schematron file name
        :returns: XSLT filename
        """
        try:
            os.makedirs(self._cachepath)
        except OSError:
            if not os.path.isdir(self._cachepath):
                raise

        schema_digest = hexdigest(schematron_schema, self._extra_hash)
        schema_basename = os.path.basename(schematron_schema)

        return os.path.join(self._cachepath, '%s.%s.validator.xsl' % (
            schema_basename, schema_digest))


class SchematronValidatorError(Exception):
    """Throw error in compilation failure
    """
    pass
