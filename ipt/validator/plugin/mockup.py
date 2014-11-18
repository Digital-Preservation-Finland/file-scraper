import ipt.validator.plugin.jhove


class ValidatorMockup(ipt.validator.plugin.jhove.Jhove):

    def __init__(self, return_values=(0, "", "")):
        self.success = return_values[0]
        self.report = return_values[1]
        self.error = return_values[2]

    def validate_file(self, mimetype, fileversion, filename):
        return (self.success, self.report, self.error)
