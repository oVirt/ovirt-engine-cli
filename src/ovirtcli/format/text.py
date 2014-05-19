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


import datetime
import sys

from ovirtcli.format.format import Formatter

from ovirtsdk.xml import params
from ovirtsdk.infrastructure.common import Base
from ovirtsdk.infrastructure import brokers
import types
from ovirtsdk.xml.params import ApiSummary


class FormatMode():
    FULL, REDUCED = range(2)

    def __init__(self, Type):
        self.value = Type

    def __str__(self):
        if self.value == FormatMode.FULL:
            return 'FULL'
        if self.value == FormatMode.REDUCED:
            return 'REDUCED'

    def __eq__(self, y):
        return self.value == y.value

class TextFormatter(Formatter):
    """Text formatter."""

    name = 'text'

    # list of complex types that should be treated as
    # primitives (e.g should be wrapped to string at runtime)
    complex_type_exceptions = [datetime.datetime]


    def _get_fields(self, typ):
        assert typ is not None
        return typ.__dict__.keys()

    def sort_fields(self, lst, strategy=[]):
        out = sorted(lst)
        for i in range(len(strategy)):
            if strategy[i] in out:
                out.remove(strategy[i])
                out.insert(i, strategy[i])

        return out

    def __get_max_field_width(self, resource, fields_exceptions, width= -1, show_empty=False, resource_context=None, mode=FormatMode.FULL):
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
                        if (value == None or value == '') and show_empty == False:
                            continue
                        new_field = field if resource_context is None else resource_context.lower() + '.' + field
                        width0 = max(width0, len(new_field))
                else:
                    value_type = type(value)
                    if (hasattr(params, value_type.__name__) \
                        and value_type not in TextFormatter.complex_type_exceptions) \
                        or hasattr(brokers, value_type.__name__):

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
                    if (value == None or value == '') and show_empty == False:
                        continue
                    new_field = field if resource_context is None else resource_context.lower() + '.' + field
                    width0 = max(width0, len(new_field))
        return width0

    def __write_context(self, format0, field, value, resource_context, reduced_mode_fields, mode=FormatMode.FULL, resource=None, parent=None):
        context = self.context
        stdout = context.terminal.stdout

        # Statistic values are always represented as floating point numbers,
        # even if they are declared as integers, so in order to render them
        # correctly we need to do a type conversion:
        if type(parent) == params.Values and type(resource) == params.Value:
            if parent.get_type() == "INTEGER":
                value = long(value)

        if type(value) == types.UnicodeType:
            val = value
        else:
            val = str(value)
        fil = (field if resource_context is None
                     else resource_context.lower() + '.' + field)\
              .replace('.', '-')
        fil = fil[:len(fil) - 1] if fil.endswith('_') \
                                     else fil

        if mode != FormatMode.REDUCED or fil in reduced_mode_fields:
            stdout.write(format0 % fil)
            stdout.write(': ')
            stdout.write(val)
            stdout.write('\n')

    def _format_resource(self, resource, width= -1, show_empty=False, resource_context=None, mode=FormatMode.FULL, sort_strategy=['id', 'name', 'description'], parent=None):
        context = self.context
        settings = context.settings
        stdout = context.terminal.stdout
        fields_exceptions = ['link', 'href', 'parentclass', '_Base__context']
        reduced_mode_fields = ['id', 'name', 'description']

        fields = self.sort_fields(self._get_fields(resource), sort_strategy)
        width0 = width

        if width0 == -1:
            if mode == FormatMode.FULL:
                width0 = self.__get_max_field_width(resource,
                                                    fields_exceptions,
                                                    width, show_empty,
                                                    resource_context,
                                                    mode=mode)
            else:
                for item in reduced_mode_fields:
                    width0 = max(width0, len(item))

        format0 = '%%-%ds' % width0

        for field in fields:
            if field not in fields_exceptions:

                value = getattr(resource, field)
                if type(value) in TextFormatter.complex_type_exceptions:
                    value = str(value)

                if isinstance(value, list):
                    value_list = value
                    for item in value_list:
                        value = item
                        if hasattr(params, type(value).__name__) or hasattr(brokers, type(value).__name__):
                            if resource_context is not None:
                                self._format_resource(resource=value,
                                                      width=width0,
                                                      show_empty=show_empty,
                                                      resource_context=(resource_context + '.' + field),
                                                      mode=mode,
                                                      parent=resource)
                            else:
                                self._format_resource(resource=value,
                                                      width=width0,
                                                      show_empty=show_empty,
                                                      resource_context=field,
                                                      mode=mode,
                                                      parent=resource)
                            continue
                        if value == None and show_empty == True:
                            value = ''
                        elif value == None: continue
                        self.__write_context(format0, field, value, resource_context, reduced_mode_fields=reduced_mode_fields, mode=mode, parent=parent, resource=resource)
                else:
                    if hasattr(params, type(value).__name__) or hasattr(brokers, type(value).__name__):
                        if resource_context is not None:
                            self._format_resource(resource=value,
                                                  width=width0,
                                                  show_empty=show_empty,
                                                  resource_context=(resource_context + '.' + field),
                                                  mode=mode,
                                                  parent=parent)
                        else:
                            self._format_resource(resource=value,
                                                  width=width0,
                                                  show_empty=show_empty,
                                                  resource_context=field,
                                                  mode=mode,
                                                  parent=parent)
                        continue
                    if value == None and show_empty == True:
                        value = ''
                    elif value == None: continue
                    self.__write_context(format0, field, value, resource_context, reduced_mode_fields=reduced_mode_fields, mode=mode, parent=parent, resource=resource)

    def _get_max_field_width_in_collection(self, collection, mode):
        fields_exceptions = ['link', 'href', 'parentclass', '_Base__context']
        reduced_mode_fields = ['id', 'name', 'description']
        width = -1
        width_static = -1

        if mode != FormatMode.FULL:
            for item in reduced_mode_fields:
                width_static = max(width_static, len(item))
            return width_static

        for resource in collection:
            width_dynamic = -1
            width_dynamic = self.__get_max_field_width(
                            resource,
                            fields_exceptions,
                            mode=mode
            )
            width = max(width, width_dynamic)
        return width

    def _format_collection(self, collection, show_empty=False):
        context = self.context
        stdout = context.terminal.stdout
        mode = FormatMode.REDUCED if not show_empty else FormatMode.FULL
        width = self._get_max_field_width_in_collection(collection, mode)
        for resource in collection:
            if isinstance(resource, Base):
                self._format_resource(resource=resource.superclass,
                                      width=width,
                                      mode=mode)
            else:
                self._format_resource(resource=resource,
                                      width=width,
                                      mode=mode)
            stdout.write('\n')

    def format(self, context, result, show_all=False):
        RESOURCE_EXCEPTIONS = [ApiSummary]
        COLLECTION_EXCEPTIONS = []
        self.context = context

        if isinstance(result, params.BaseResource) or type(result) in RESOURCE_EXCEPTIONS:
            if isinstance(result, Base):
                context.terminal.stdout.write('\n')
                self._format_resource(result.superclass, show_empty=show_all)
                context.terminal.stdout.write('\n')
            else:
                context.terminal.stdout.write('\n')
                self._format_resource(resource=result, show_empty=show_all)
                context.terminal.stdout.write('\n')
        elif isinstance(result, list) or type(result) in COLLECTION_EXCEPTIONS:
            context.terminal.stdout.write('\n')
            self._format_collection(collection=result, show_empty=show_all)
#            context.terminal.stdout.write('\n')
