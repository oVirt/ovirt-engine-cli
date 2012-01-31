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

from ovirtsdk.xml import params
from ovirtsdk.utils.parsehelper import ParseHelper
from ovirtsdk.infrastructure.common import Base
from ovirtsdk.infrastructure import brokers


class TextFormatter(Formatter):
    """Text formatter."""

    name = 'text'

    def _get_fields(self, typ):
        assert typ is not None
        return typ.__dict__.keys()

    def __get_max_field_width(self, resource, fields_exceptions, width= -1, show_empty=False, resource_context=None):
        new_field = None
        width0 = width

        for field in self._get_fields(resource):
            if field not in fields_exceptions:
                value = resource.__dict__[field]
                if isinstance(value, list):
                    value_list = value
                    for item in value_list:
                        value = item
                        if hasattr(params, type(value).__name__) or hasattr(brokers, type(value).__name__):
                            if resource_context is not None:
                                width0 = max(width0, self.__get_max_field_width(resource=value,
                                                                                fields_exceptions=fields_exceptions,
                                                                                width=width0,
                                                                                show_empty=show_empty,
                                                                                resource_context=(resource_context + '.' + field)))
                            else:
                                width0 = max(width0, self.__get_max_field_width(resource=value,
                                                                                fields_exceptions=fields_exceptions,
                                                                                width=width0,
                                                                                show_empty=show_empty,
                                                                                resource_context=field))
                            continue
                        if not value and show_empty == False:
                            continue
                        new_field = field if resource_context is None else resource_context.lower() + '.' + field
                        width0 = max(width0, len(new_field))
                else:
                    if hasattr(params, type(value).__name__) or hasattr(brokers, type(value).__name__):
                        if resource_context is not None:
                            width0 = max(width0, self.__get_max_field_width(resource=value,
                                                                            fields_exceptions=fields_exceptions,
                                                                            width=width0,
                                                                            show_empty=show_empty,
                                                                            resource_context=(resource_context + '.' + field)))
                        else:
                            width0 = max(width0, self.__get_max_field_width(resource=value,
                                                                            fields_exceptions=fields_exceptions,
                                                                            width=width0,
                                                                            show_empty=show_empty,
                                                                            resource_context=field))
                        continue
                    if not value and show_empty == False:
                        continue
                    new_field = field if resource_context is None else resource_context.lower() + '.' + field
                    width0 = max(width0, len(new_field))
        return width0

    def __write_context(self, format0, format1, width1, field, value, resource_context):
        context = self.context
        stdout = context.terminal.stdout

        stdout.write(format0 % (field if resource_context is None else resource_context.lower() + '.' + field))
        stdout.write(': ')
        stdout.write(format1 % str(value))
        stdout.write('\n')
        value = str(value)[width1:]
        while len(str(value)) > 0:
            stdout.write(width1 * ' ')
            stdout.write(format1 % str(value))
            stdout.write('\n')
            value = str(value)[width1:]

    def _format_resource(self, resource, width= -1, show_empty=False, resource_context=None):
        context = self.context
        settings = context.settings
        stdout = context.terminal.stdout
        fields_exceptions = ['link', 'href']

        fields = self._get_fields(resource)
        width0 = width

        if width0 == -1:
            width0 = self.__get_max_field_width(resource, fields_exceptions, width, show_empty, resource_context)

        format0 = '%%-%ds' % width0
        if stdout.isatty() and not settings['ovirt-shell:wide']:
            width1 = context.terminal.width - width0 - 2
            format1 = '%%-%d.%ds' % (width1, width1)
        else:
            width1 = sys.maxint
            format1 = '%s'

        for field in fields:
            if field not in fields_exceptions:
                value = resource.__dict__[field]
                if isinstance(value, list):
                    value_list = value
                    for item in value_list:
                        value = item
                        if hasattr(params, type(value).__name__) or hasattr(brokers, type(value).__name__):
                            if resource_context is not None:
                                self._format_resource(resource=value,
                                                      width=width0,
                                                      show_empty=show_empty,
                                                      resource_context=(resource_context + '.' + field))
                            else:
                                self._format_resource(resource=value,
                                                      width=width0,
                                                      show_empty=show_empty,
                                                      resource_context=field)
                            continue
                        if not value and show_empty == True:
                            value = ''
                        elif not value: continue
                        self.__write_context(format0, format1, width1, field, value, resource_context)
                else:
                    if hasattr(params, type(value).__name__) or hasattr(brokers, type(value).__name__):
                        if resource_context is not None:
                            self._format_resource(resource=value,
                                                  width=width0,
                                                  show_empty=show_empty,
                                                  resource_context=(resource_context + '.' + field))
                        else:
                            self._format_resource(resource=value,
                                                  width=width0,
                                                  show_empty=show_empty,
                                                  resource_context=field)
                        continue
                    if not value and show_empty == True:
                        value = ''
                    elif not value: continue
                    self.__write_context(format0, format1, width1, field, value, resource_context)

        #stdout.write('\n')

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

    def format(self, context, result, show_all=False):
        self.context = context
        if isinstance(result, params.BaseResource):
            if isinstance(result, Base):
                self._format_resource(result.superclass, show_empty=show_all)
            else:
                self._format_resource(resource=result, show_empty=show_all)
        elif isinstance(result, list):
            self._format_collection(resource=result, show_empty=show_all)
