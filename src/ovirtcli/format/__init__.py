
from ovirtcli.format.format import Formatter
from ovirtcli.format.xml_ import XmlFormatter
from ovirtcli.format.text import TextFormatter


def get_formatter(format):
    """Return the formatter class for `format', or None if it doesn't exist."""
    for sym in globals():
        obj = globals()[sym]
        if isinstance(obj, type) and issubclass(obj, Formatter) \
                and obj.name == format:
            return obj
