import sys
import os
import os.path
import json
import time
from pprint import pprint
#import antigravity

import trace

from datetime import datetime
import subprocess
from doctest import REPORT_CDIFF

import ipt
import ipt.validator.plugin.jhove
import ipt.validator.plugin.jhove2
import ipt.validator.plugin.libxml
import ipt.validator.plugin.filecommand

CONFIG_FILENAME = os.path.join('/usr/share/',
                               'information-package-tools/validators',
                               'validators.json')


class FileInfo:

    format_version = None
    format_registry_key = None
    filename = None
    digest_hex = None
    digest_algorithm = None
    object_id = ""

    def __init__(self, fileinfo=None):
        if type(fileinfo) is dict:
            self.from_dict(fileinfo)
        if type(fileinfo) is list:
            self.from_array(fileinfo)

    def from_array(self, fileinfo):
        # FIXME: replace fileinfo array with dict
        self.filename = fileinfo[0]
        self.digest_algorithm = fileinfo[1]
        self.digest_hex = fileinfo[2]
        self.format_mimetype = fileinfo[3]
        self.format_version = fileinfo[4]
        self.format_registry_key = fileinfo[5]
        if len(fileinfo) > 6:
            self.object_id = dict()
            self.object_id['type'] = fileinfo[6]
        if len(fileinfo) > 7:
            self.object_id['value'] = fileinfo[7]

    def from_dict(self, fileinfo):
        self.filename = fileinfo['filename']
        self.object_id = fileinfo['object_id']

        self.digest_algorithm = fileinfo['fixity']['algorithm']
        self.digest_hex = fileinfo['fixity']['digest']
        self.format_mimetype = fileinfo['format']['mimetype']
        self.format_version = fileinfo['format']['version']
        self.format_registry_key = fileinfo['format']['registery_key']

    def __str__(self):
        return "ipt.validator.plugin.FileInfo(%s, %s, %s, %s, %s, %s, %s)" % (
            self.filename, self.digest_algorithm, self.digest_hex,
            self.format_mimetype, self.format_version,
            self.format_registry_key, self.object_id)


class Validator:

    def __init__(self, base_path=""):
        self.basepath = base_path
        self.validators_config = None

    def load_config(self, config_filename=None):
        if config_filename is None:
            config_filename = CONFIG_FILENAME
        json_data = open(config_filename)
        self.validators_config = json.load(json_data)
        json_data.close()

    def get_class_instance_by_name(self, path, params):
        """ Return instance of class declared in path argument """

        modules = path.split(".")
        instance = globals()[modules[0]]

        for module in modules[1:]:
            instance = getattr(instance, module)

        if params:
            return instance(*params)

        return instance()

    def validate_file(self, fileinfo, validator_name, validator_params=None):
        validator_params = (fileinfo.format_mimetype,
                            fileinfo.format_version,
                            os.path.join(self.basepath,
                                         fileinfo.filename))

        validate = self.get_class_instance_by_name(
            validator_name, validator_params)

        (returnstatus, messages, errors) = validate.validate()

        return (returnstatus, messages, errors)

    def get_validators(self, fileinfo):
        """ Return list of possible validators for filetype and version """

        found_validators = []

        for config in self.validators_config["formatNameList"]:
            for format_mimetype, validator_configs in config.iteritems():
                if fileinfo.format_mimetype == format_mimetype:
                    for validator in validator_configs:
                        if fileinfo.format_version == \
                                validator["formatVersion"]:
                            if len(validator["validator"]) > 0:
                                found_validators.append(validator["validator"])

        return found_validators

    def validate_files(self, filelist):
        """
        Calls validator selector function for each file in SIPs manifest file
        """
        return_status = []
        messages = []
        errors = []
        validators = []

        # Check that there are no extra or missing files
        # in mets <mets:FLocat>-field
        found_files = []
        for directory, _, files in os.walk(self.basepath):
            for file_name in files:
                file_rel_path = self.get_file_rel_dir_path(
                    directory, file_name)
                found_files.append(str(file_rel_path))

        filelist_files = []
        for file_ in filelist:
            filelist_files.append(str(file_[0]))
        if set(found_files) != set(filelist_files):
            return (
                [117],
                ["Validation error",
                 "Extranous or missing files in <mets:FLocat>-field"],
                ["Extranous or missing files in <mets:FLocat>-field"],
                [None])

        # Validate files
        for file_ in filelist:

            fileinfo = FileInfo(file_)
            validators_for_file = self.get_validators(fileinfo)
            if len(validators_for_file) == 0:
                error = \
                    'INVALID:%s:No validator for mimetype:%s version:%s' % (
                    fileinfo.filename, fileinfo.format_mimetype,
                    fileinfo.format_version)

                validators.append("")
                return_status.append(1)
                messages.append("\n")
                errors.append(error)

            for validator in validators_for_file:
                (status, message, error) = self.validate_file(
                    fileinfo, validator)
                validators.append(validator)
                return_status.append(status)
                messages.append(message)
                errors.append(error)

        return (return_status, messages, errors, validators)


    def get_file_rel_dir_path(self, directory, filename):
        """ util function get file relative path inside sip.
        :directory: base directory path of the SIP.
        :filename: base name of the digital object"""
        processing_directory = os.path.dirname(self.basepath) + "/"
        file_rel_path_with_sip_dir = directory.replace(
            processing_directory, "")
        slash_location = file_rel_path_with_sip_dir.find("/")
        if slash_location == -1:
            file_rel_path = ""
        else:
            file_rel_path = file_rel_path_with_sip_dir[
                slash_location+1 : len(file_rel_path_with_sip_dir)-1]

        return  os.path.join(file_rel_path, str(filename))
