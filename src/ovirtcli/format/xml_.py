
import re
from xml.dom import minidom

from ovirtcli.format.format import Formatter

# This module is called xml_ to prevent a naming conflict with the standard
# libary.


class XmlFormatter(Formatter):
    """XML formatter."""

    name = 'xml'

    _re_spacing1 = re.compile('(>)\n\s+([^<\s])')
    _re_spacing2 = re.compile('([^>])\n\s+(<)')

    def format(self, context, result, scope=None):
        if not hasattr(result, 'toxml'):
            raise TypeError, 'Expecting a binding instance.'
        self.context = context
        stdout = context.terminal.stdout
        buf = result.toxml()
        xml = minidom.parseString(buf)
        buf = xml.documentElement.toprettyxml(indent='  ')
        # XXX: These strings substituations are not context-sensitive
        # and may introduce issues. It removes illegal spacing that
        # .toprettyxml() is adding.
        buf = self._re_spacing1.sub(r'\1\2', buf)
        buf = self._re_spacing2.sub(r'\1\2', buf)
        stdout.write(buf)
