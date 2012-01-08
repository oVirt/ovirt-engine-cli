#
# Copyright (c) 2010 Red Hat, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#           http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#


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
