
class RootException(Exception):
    def __init__(self, detail):
        self.what = ''
        self.detail = detail

    def __str__(self):
        return '%s/%s' % (self.what, self.detail)


class SAMUError(RootException):
    def __init__(self, detail):
        super(SAMUError, self).__init__(detail)
        self.what = 'samu error'


