import os
import shutil
import tempfile
import subprocess

import ipt.fileutils.checksum

import xml.etree.ElementTree

"""

Schematron validation using iso-schematron-xslt1 reference implementation.

XSLT template converts are done with xsltproc / libxslt C Library for
Gnome. This is because Python xml libraries are not stable enough for
Schematron.

    http://xmlsoft.org/XSLT/

Schematron XSLT files must be installed at path

    /usr/share/schematron/iso-schematron-xslt1/

Schematron XSLT files can be downloaded from

    http://www.schematron.com/implementation.html

Schematron templates are cached at

    /tmp/iso-schematron-xslt1/<md5 of schematron schema>.xslt

This reduces need to sequentially compile Schematron schemas into XSLT
templates.

"""


class ValidationResult:
    returncode = None
    messages = None
    errors = None

    def __init__(self, returncode, messages, errors):
        self.returncode = returncode
        self.messages = messages
        self.errors = errors

    def format_messages(self):

        tree = xml.etree.ElementTree.fromstring(self.messages)

        ns = '{http://purl.oclc.org/dsdl/svrl}'
        failed_asserts = tree.findall('%sfailed-assert' % ns)

        messages = []

        for failed_assert in failed_asserts:

            elem_text = failed_assert.find('%stext' % ns)
            elem_line = failed_assert.find('%sline-number' % ns)

            message = ''
            if elem_text is not None:
                message = 'Error: %s' % elem_text.text.strip()
            if elem_line is not None:
                message = '%s [Line: %s]' % (message, elem_line.text.strip())
            messages.append(message)

        return '\n'.join(messages)

    def format_errors(self):
        return self.errors

    def has_errors(self):
        return self.messages.find('<svrl:failed-assert ') >= 0

    def __str__(self):
        if self.returncode == 0:
            return ""
        else:
            return self.format_errors()


class XSLT:

    def __init__(self, cache=False):
        self.cache = cache
        self.schematron_version = 1
        self.sharepath = '/usr/share/information-package-tools'
        self.cachepath = os.path.expanduser('~/.information-package-tools/'
                                            'schematron-cache')

    def validate_file(self, schematron_schema, xml_file):

        with tempfile.NamedTemporaryFile() as tmpfile:

            xslt_filename = self.schematron_to_xslt(schematron_schema)

            # Debug
            # print "xslt", xslt_filename, "xml", xml_file, "result",
            # tmpfile.name

            # Step 4 - Validate XML file with Schematron XSLT transformation (
            result = self.xslt_convert(
                xslt_filename, xml_file, tmpfile.name)

            result.errors = '\n'.join([result.messages, result.errors])

            f = open(tmpfile.name)
            result.messages = f.read()
            f.close()

            return ValidationResult(result.returncode,
                                    result.messages, result.errors)

    def schematron_to_xslt(self, schematron_schema):

        tempdir = tempfile.mkdtemp()

        try:

            xslt_filename = self.generate_xslt_filename(schematron_schema)

            if self.cache:
                if os.path.isfile(xslt_filename):
                    # FIXME KDKPAS-668 Returning an undefined variable!
                    return xslt_cached_filename

            # Step 1 - Add Schematron include rules ( schema.sch -> step1.xsl )
            result = self.xslt_convert(
                'iso_dsdl_include.xsl',
                schematron_schema,
                os.path.join(tempdir, 'step1.xsl'))

            # Step 2 - Expand arguments ( step1.xsl -> step2.xsl )
            result = self.xslt_convert(
                'iso_abstract_expand.xsl',
                os.path.join(tempdir, 'step1.xsl'),
                os.path.join(tempdir, 'step2.xsl'))

            # Step 3 - Generage xsl file for validating XML ( step3.xsl ->
            # schema.sch.<sha digest>.xsl )
            result = self.xslt_convert(
                'iso_svrl_for_xslt%s.xsl' % self.schematron_version,
                os.path.join(tempdir, 'step2.xsl'),
                os.path.join(tempdir, 'validator.xsl'))

            shutil.move(os.path.join(tempdir, 'validator.xsl'),
                        xslt_filename)

            return xslt_filename

        finally:
            shutil.rmtree(tempdir)

    def xslt_convert(self, xslt_template, input_filename, output_filename):

        schematron_dirname = 'iso-schematron-xslt%s' % (
            self.schematron_version)
        schematron_xslt_path = os.path.join(self.sharepath, 'schematron',
                                            schematron_dirname)

        xslt_template = os.path.join(schematron_xslt_path, xslt_template)

        cmd = ['xsltproc', '-o', output_filename, xslt_template,
               input_filename]

        p = subprocess.Popen(cmd, stdin=subprocess.PIPE,
                             stderr=subprocess.PIPE, stdout=subprocess.PIPE,
                             close_fds=False, shell=False)

        (stdout, stderr) = p.communicate()

        if p.returncode != 0:
            raise Exception("Error %s\nstdout:\n%s\nstderr\n%s" % (
                            p.returncode, stdout, stderr))

        return ValidationResult(p.returncode, stdout, stderr)

    def generate_xslt_filename(self, schematron_schema):
        """ Example filename:

            /var/cache/schematron-validation/<schema.sch>.<sha digest>.xslt

        """
        if not os.path.exists(self.cachepath):
            os.makedirs(self.cachepath)

        checksum = ipt.fileutils.checksum.BigFile('sha1')
        schema_digest = checksum.hexdigest(schematron_schema)
        schema_basename = os.path.basename(schematron_schema)

        return os.path.join(self.cachepath, '%s.%s.validator.xsl' % (
                            schema_basename, schema_digest))

    def clear_xslt_cache(self):
        shutil.rmtree(os.path.join(self.cachepath, '*'))
