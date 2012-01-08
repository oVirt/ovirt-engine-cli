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


import sys

from ovirtcli.format.format import Formatter
from ovirtcli import metadata

from ovirtsdk.xml import params
from ovirtsdk.utils.parsehelper import ParseHelper
from ovirtsdk.infrastructure.common import Base


class TextFormatter(Formatter):
    """Text formatter."""

    name = 'text'

    def _get_fields(self, typ, flag, scope=None):
        #info = schema.type_info(typ)
        #collection_member = type(typ).__name__.lower()[0 : len(type(typ).__name__) - 1]
#        assert info is not None
#        override = self.context.settings.get('ovirt-shell:fields.%s' % info[2])
        assert typ is not None
        override = self.context.settings.get('ovirt-shell:fields.%s' % type(typ).__name__)
        if override is None:
            override = self.context.settings.get('ovirt-shell:fields')
        if override is None:
            fields = metadata.get_fields(typ, flag, scope)
        else:
            override = override.split(',')
            fields = metadata.get_fields(typ, '')
            fields = filter(lambda f: f.name in override, fields)
        return fields

    def _format_resource(self, resource, scope=None):
        context = self.context
        settings = context.settings
        stdout = context.terminal.stdout
        fields = self._get_fields(type(resource), 'S', scope)
        width0 = 0
        for field in fields:
            width0 = max(width0, len(field.name))
        format0 = '%%-%ds' % width0
        if stdout.isatty() and not settings['ovirt-shell:wide']:
            width1 = context.terminal.width - width0 - 2
            format1 = '%%-%d.%ds' % (width1, width1)
        else:
            width1 = sys.maxint
            format1 = '%s'
        stdout.write('\n')
        for field in fields:
            value = field.get(resource, self.context)
            if not value:
                continue
            stdout.write(format0 % field.name)
            stdout.write(': ')
            stdout.write(format1 % value)
            stdout.write('\n')
            value = value[width1:]
            while len(value) > 0:
                stdout.write(width1 * ' ')
                stdout.write(format1 % value)
                stdout.write('\n')
                value = value[width1:]
        stdout.write('\n')

    def _format_collection(self, collection, scope=None):
        context = self.context
        settings = context.settings
        stdout = context.terminal.stdout

#FIXME: add attribute/field overriding caps as in self._get_fields()
#        info = schema.type_info(type(collection))
#        fields = self._get_fields(info[0], 'L', scope)

#        collection_name = type(collection).__name__
#        if collection_name.endswith('s'):
#            candidate = collection_name[0 : len(collection_name) - 1]
#        else:
#            candidate = collection_name
        if len(collection) == 0: return
        fields = self._get_fields(params.findRootClass(ParseHelper.getXmlTypeInstance(type(collection[0].superclass).__name__.lower())),
                                                                                      'L',
                                                                                      scope)
#        collection_member = ParseHelper.getSingularXmlTypeInstance(type(collection).__name__)

        # Calculate the width of each column
#        widths = [ len(f.name) for f in fields ]

        if fields != None and len(fields) > 0:
            widths = [ len(f.name) for f in fields ]
#        for resource in getattr(collection, collection_member):
            for resource in collection:
                for i in range(len(fields)):
                    value = fields[i].get(resource, self.context)
                    widths[i] = max(widths[i], len(value))
            total = sum(widths) + 2 * len(fields)
            # Now downsize if it doesn't fit
            if stdout.isatty() and not settings['ovirt-shell:wide'] and \
                    total > context.terminal.width:
                fraction = 1.0 * context.terminal.width / total
                fwidths = [0] * len(fields)
                # Pass 1: round down to nearest integer
                for i in range(len(fields)):
                    fwidths[i] = widths[i] * fraction
                    widths[i] = int(fwidths[i])
                # Pass 2: allocate fractional leftovers to columns
                available = context.terminal.width - 2 * len(fields) - sum(widths)
                remainders = [ (fwidths[i] - widths[i], i) for i in range(len(fields)) ]
                remainders.sort(reverse=True)
                for i in range(min(len(fields), available)):
                    widths[remainders[i][1]] += 1
            formats = ['%%-%d.%ds' % (w, w) for w in widths ]
            if settings['ovirt-shell:header']:
                # Header
                for i in range(len(fields)):
                    stdout.write(formats[i] % fields[i].name)
                    if i != len(fields) - 1:
                        stdout.write('  ')
                stdout.write('\n')
                # Horizontal line
                for i in range(len(fields)):
                    stdout.write('-' * widths[i])
                    if i != len(fields) - 1:
                        stdout.write('  ')
                stdout.write('\n')
            # Data elements
#        for resource in getattr(collection, collection_member):
            for resource in collection:
                values = [ field.get(resource, self.context) for field in fields ]
                while sum([len(v) for v in values]) > 0:
                    for i in range(len(fields)):
                        stdout.write(formats[i] % values[i])
                        values[i] = values[i][widths[i]:]
                        if i != len(fields) - 1:
                            stdout.write('  ')
                    stdout.write('\n')
            stdout.write('\n')

    def format(self, context, result, scope=None):
##        if isinstance(result, schema.BaseResource):
#        if isinstance(result, params.BaseResource):
#            self._format_resource(result, scope)
##        elif isinstance(result, schema.BaseResources):
#        elif isinstance(result, params.BaseResources):
#            self._format_collection(result, scope)

        self.context = context
        if isinstance(result, params.BaseResource):
            if isinstance(result, Base):
                self._format_resource(result.superclass, scope)
            else:
                self._format_resource(result, scope)
        elif isinstance(result, list):
            self._format_collection(result, scope)
