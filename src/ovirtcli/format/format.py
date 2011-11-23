
class Formatter(object):
    """Base class for formatter objects."""

    name = None

    def format(self, context, result, scope=None):
        raise NotImplementedError
