
class ipamCLIException(Exception):
    message = 'An unknown exception occurred.'

    def __init__(self, message=None, **kwargs):
        if message:
            self.message = message
        try:
            self._error_string = self.message % kwargs
        except Exception:
            # at least get the core message out if something happened
            self._error_string = self.message

    def __str__(self):
        return self._error_string


class ipamCLIIPExists(ipamCLIException):
    pass
