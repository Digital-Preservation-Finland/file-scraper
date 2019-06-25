"""Schematron scraper."""
import os
import shutil
import tempfile
import lxml.etree as etree
from file_scraper.base import BaseScraper, ProcessRunner
from file_scraper.schematron.schematron_model import SchematronMeta
from file_scraper.utils import hexdigest, ensure_str


class SchematronScraper(BaseScraper):
    """Schematron scraper."""

    _supported_metadata = [SchematronMeta]
    _only_wellformed = True

    def __init__(self, filename, check_wellformed=True, params=None):
        """
        Initialize instance.

        :filename: File path
        :mimetype: Predicted mimetype of the file
        :check_wellformed: True for the full well-formed check, False for just
                           detection and metadata scraping
        :params: Extra parameters needed for the scraper
        """
        if params is None:
            params = {}
        self._verbose = params.get("verbose", False)
        self._cache = params.get("cache", True)
        self._cachepath = os.path.expanduser(
            "~/.file-scraper/schematron-cache")
        self._schematron_dirname = "/usr/share/iso_schematron_xslt1"
        self._returncode = None
        self._schematron_file = params.get("schematron", None)
        self._extra_hash = params.get("extra_hash", None)
        super(SchematronScraper, self).__init__(filename, check_wellformed,
                                                params)

    @classmethod
    def is_supported(cls, mimetype, version=None,
                     check_wellformed=True, params=None):
        """
        Return True if the MIME type and version are supported.

        We use this scraper only with a schematron file.

        :mimetype: Identified mimetype
        :version: Identified version (if needed)
        :check_wellformed: True for the full well-formed check, False for just
                           detection and metadata scraping
        :params: Extra parameters needed for the scraper
        :returns: True if scraper is supported
        """
        if params is None:
            params = {}
        if "schematron" not in params:
            return False
        return super(SchematronScraper, cls).is_supported(
            mimetype, version, check_wellformed, params)

    @property
    def well_formed(self):
        """Check if document resulted errors."""
        if not self._check_wellformed:
            return None
        if not self.errors() and self.messages():
            if self.messages().find("<svrl:failed-assert ") < 0 \
                    and self._returncode == 0:
                return True
        return False

    def scrape_file(self):
        """Do the Schematron check."""
        if not self._check_wellformed and self._only_wellformed:
            self._messages.append("Skipping scraper: Well-formed check not "
                                  "used.")
            return

        if self._schematron_file is None:
            self._errors.append("Schematron file missing from parameters.")
            return

        xslt_filename = self._compile_schematron()

        shell = self._compile_phase(
            stylesheet=xslt_filename,
            inputfile=self.filename, allowed_codes=[0, 6])

        self._returncode = shell.returncode
        if shell.stderr:
            self._errors.append(ensure_str(shell.stderr))

        if not self._verbose and shell.returncode == 0:
            self._messages.append(
                ensure_str(self._filter_duplicate_elements(shell.stdout)))
        else:
            self._messages.append(ensure_str(shell.stdout))

        for md_class in self._supported_metadata:
            self.streams.append(md_class())

        self._check_supported(allow_unav_mime=True, allow_unav_version=True)

    # pylint: disable=no-self-use
    def _filter_duplicate_elements(self, result):
        """
        Filter duplicate elements from the result.

        :result: Result as string
        """
        svrl = {"svrl": "http://purl.oclc.org/dsdl/svrl"}
        root = etree.fromstring(result)
        patterns = root.xpath("./svrl:active-pattern", namespaces=svrl)
        for pattern in patterns:
            prev = pattern.xpath("preceding-sibling::svrl:active-pattern[1]",
                                 namespaces=svrl)
            if prev and pattern.get("id") == prev[0].get("id"):
                pattern.getparent().remove(pattern)

        rules = root.xpath("svrl:fired-rule", namespaces=svrl)
        for rule in rules:
            prev = rule.xpath("preceding-sibling::svrl:fired-rule[1]",
                              namespaces=svrl)
            if prev and rule.get("context") == prev[0].get("context"):
                rule.getparent().remove(rule)

        return etree.tostring(
            root, pretty_print=True, xml_declaration=False,
            encoding="UTF-8", with_comments=True)

    # pylint: disable=too-many-arguments
    def _compile_phase(self, stylesheet, inputfile, allowed_codes,
                       outputfile=None, outputfilter=False):
        """
        Compile one phase.

        :stylesheet: XSLT file to used in the conversion
        :inputfile: Input document filename
        :outputfile: Filename of the resulted document, stdout if None
        :outputfilter: Use outputfilter parameter with value only_messages
        :return: ProcessRunner instance
        """
        cmd = ["xsltproc"]
        if outputfile:
            cmd = cmd + ["-o", outputfile]
        if outputfilter and not self._verbose:
            cmd = cmd + ["--stringparam", "outputfilter", "only_messages"]
        cmd = cmd + [os.path.join(self._schematron_dirname, stylesheet),
                     inputfile]
        shell = ProcessRunner(cmd)
        if shell.returncode not in allowed_codes:
            raise SchematronValidatorError(
                "Error %s\nstdout:\n%s\nstderr:\n%s" % (
                    shell.returncode, ensure_str(shell.stdout),
                    ensure_str(shell.stderr)))
        return shell

    def _compile_schematron(self):
        """
        Compile a schematron file.

        :returns: XSLT file name
        """
        xslt_filename = self._generate_xslt_filename()
        tempdir = tempfile.mkdtemp()

        if self._cache:
            if os.path.isfile(xslt_filename):
                return xslt_filename

        try:
            self._compile_phase(
                stylesheet="iso_dsdl_include.xsl",
                inputfile=self._schematron_file,
                outputfile=os.path.join(tempdir, "step1.xsl"),
                allowed_codes=[0])
            self._compile_phase(
                stylesheet="iso_abstract_expand.xsl",
                inputfile=os.path.join(tempdir, "step1.xsl"),
                outputfile=os.path.join(tempdir, "step2.xsl"),
                allowed_codes=[0])
            self._compile_phase(
                stylesheet="optimize_schematron.xsl",
                inputfile=os.path.join(tempdir, "step2.xsl"),
                outputfile=os.path.join(tempdir, "step3.xsl"),
                allowed_codes=[0])
            self._compile_phase(
                stylesheet="iso_svrl_for_xslt1.xsl",
                inputfile=os.path.join(tempdir, "step3.xsl"),
                outputfile=os.path.join(tempdir, "validator.xsl"),
                outputfilter=not (self._verbose),
                allowed_codes=[0])

            shutil.move(os.path.join(tempdir, "validator.xsl"),
                        xslt_filename)

        finally:
            shutil.rmtree(tempdir)

        return xslt_filename

    def _generate_xslt_filename(self):
        """
        Generate XSLT filename from schematron file.

        :returns: XSLT filename
        """
        try:
            os.makedirs(self._cachepath)
        except OSError:
            if not os.path.isdir(self._cachepath):
                raise
        extra = ""
        if self._verbose:
            extra = "verbose"
        if self._extra_hash is not None:
            extra = "%s%s" % (extra, self._extra_hash)
        schema_digest = hexdigest(self._schematron_file, extra_hash=extra)
        schema_basename = os.path.basename(self._schematron_file)

        return os.path.join(self._cachepath, "%s.%s.validator.xsl" % (
            schema_basename, schema_digest))


class SchematronValidatorError(Exception):
    """Throw error in case of a compilation failure."""

    pass
