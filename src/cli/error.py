
from cli import compat


class Error(Exception):
    """Base class for python-cli errors."""

    def __init__(self, message=None, **kwargs):
        if message is None:
            message = self.__doc__
        compat.super(Error, self).__init__(message)
        for key in kwargs:
            setattr(self, key, kwargs[key])


class ParseError(Error):
    """Error parsing command line."""


class CommandError(Error):
    """Illegal command."""
