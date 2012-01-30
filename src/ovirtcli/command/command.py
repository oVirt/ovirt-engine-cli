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


import uuid

from ovirtcli import metadata
from cli.command import Command
from ovirtcli.utils.typehelper import TypeHelper

from ovirtsdk.xml import params
from ovirtsdk.utils.parsehelper import ParseHelper
from ovirtsdk.infrastructure import brokers
import inspect
from ovirtcli.utils.methodhelper import MethodHelper


class OvirtCommand(Command):
    """Base class for oVirt commands."""

    def check_connection(self):
        """ensure we have a connection."""
        if self.context.connection is None:
            self.error('not connected', help='try \'help connect\'')
        return self.context.connection

    def resolve_base(self, options):
        """resolve a base object from a set of '--typeid value' options."""
        connection = self.check_connection()

        for opt, val in options.items():
            if not opt.endswith('id'):
                continue
            typename = opt[2:-2]
            coll = typename + 's'
            if not (TypeHelper.isKnownType(typename) or  TypeHelper.isKnownType(coll)):
                self.error('no such type: %s' % typename)

            if hasattr(connection, coll):
                coll_ins = getattr(connection, coll)
                uuid_cand = self._toUUID(val)
                if uuid_cand != None:
                    base = coll_ins.get(id=val)
                else:
                    base = coll_ins.get(name=val)

                if base is None and len(options) > 0:
                    self.error('cannot find object %s' % val)
                return base

    def create_object(self, typ, options, scope=None):
        """Create a new object of type `typ' based on the command-line
        options in `options'."""

        candidate = getattr(params, ParseHelper.getXmlWrapperType(typ))
        if candidate is not None:
            obj = candidate.factory()
            fields = metadata.get_fields(candidate, 'C', scope)
            for field in fields:
                key = '--%s' % field.name
                if key in options:
                    field.set(obj, options[key], self.context)
            return obj
        return None

    def update_object(self, obj, options, scope=None):
        """Create a new binding type of type `typ', and set its attributes
        with values from `options'."""
        fields = metadata.get_fields(type(obj.superclass), 'U', scope)
        for field in fields:
            key = '--%s' % field.name
            if key in options:
                field.set(obj, options[key], self.context)
        return obj

    def read_object(self):
        """If input was provided via stdin, then parse it and return a binding
        instance."""
        stdin = self.context.terminal.stdin
        # REVISE: this is somewhat of a hack (this detects a '<<' redirect by
        # checking if stdin is a StringIO)
        if not hasattr(stdin, 'len'):
            return
        buf = stdin.read()
        try:
            obj = params.parseString(buf)
        except Exception:
            self.error('could not parse input')
        return obj

    def get_collection(self, typ, opts=[], base=None):
        self.check_connection()
        connection = self.context.connection

        if base is None:
            if hasattr(connection, typ):
                return getattr(connection, typ).list(query=' '.join(opts) if len(opts) > 0
                                                                          else None)
        else:
            if hasattr(base, typ):
                return getattr(base, typ).list(query=' '.join(opts) if len(opts) > 0
                                                                    else None)
        return None

    def get_object(self, typ, id, base=None):
        """Return an object by id or name."""
        self.check_connection()
        connection = self.context.connection

        candidate = typ if typ is not None and isinstance(typ, type('')) \
                        else type(typ).__name__.lower()

        if base is None: base = connection
        if hasattr(base, candidate + 's'):
            coll = getattr(base, candidate + 's')
            if coll is not None:
                uuid_cand = self._toUUID(id)
                if uuid_cand != None:
                    return coll.get(id=id)
                else:
                    return coll.get(name=id)
        else:
            self.error('no such type: %s' % candidate)
        return None

    def _toUUID(self, string):
        try:
            return uuid.UUID(string)
        except:
            return None


    def _get_method_params(self, module, clazz, method, holder={}):
        args = MethodHelper.getMethodArgs(module, clazz, method)
        if args:
            if len(args) == 3:
                if not holder.has_key(args[2]):
                    holder[args[2]] = args[1]
                else:
                    if holder[args[2]] == None:
                        if args[1] != None:
                            holder[args[2]] = 'None, ' + args[1]
                    else:
                        holder[args[2]] = holder[args[2]] + ', ' + args[1]
            elif len(args) == 2:
                if not holder.has_key(args[1]):
                    holder[args[1]] = None
                else:
                    if holder[args[1]] == None:
                        if holder[args[1]] != None:
                            holder[args[1]] = 'None' + ', ' + holder[args[1]]
                    else:
                        holder[args[1]] = holder[args[1]] + ', ' + 'None'
        return holder

    def _get_types(self, plural, method):
        """INTERNAL: return a list of types that implement given method and context/s of this types."""
        sing_types = {}

        if method:
            for decorator in TypeHelper.getKnownDecoratorsTypes():
                dct = getattr(brokers, decorator).__dict__
                if dct.has_key(method):
                    if decorator.endswith('s'):
                        cls_name = TypeHelper.getDecoratorType(decorator[:len(decorator) - 1])
                        if cls_name:
                            self._get_method_params(brokers, cls_name, '__init__', sing_types)

            if plural:
                sing_types_plural = {}
                for k in sing_types.keys():
                    sing_types_plural[self.to_plural(k)] = sing_types[k]
                return sing_types_plural
            return sing_types

    def get_singular_types(self, method=None):
        """Return a list of singular types."""
        return self._get_types(False, method)

    def get_plural_types(self, method=None):
        """Return a list of plural types."""
        return self._get_types(True, method)

    def to_singular(self, string):
        if string.endswith('s'):
            return string[:len(string) - 1]
        return string

    def to_plural(self, string):
        if not string.endswith('s'):
            return string + 's'
        return string

    def get_options(self, method, resource, sub_resource=None):
        """Return a list of options for typ/action."""

        PARAM_ANNOTATION = '@param'
        method_ref = None
        connection = self.check_connection()

        if isinstance(resource, type('')):
            if not sub_resource:
                    if resource and hasattr(connection, resource + 's') and \
                       type(getattr(connection, resource + 's')).__dict__.has_key(method):
                        method_ref = getattr(getattr(connection,
                                                     resource + 's'),
                                             method)
            else:
                if hasattr(sub_resource, resource + 's') and \
                type(getattr(sub_resource, resource + 's')).__dict__.has_key(method):
                    method_ref = getattr(getattr(sub_resource,
                                                 resource + 's'),
                                         method)
                elif hasattr(sub_resource, resource + 's') and \
                hasattr(brokers, self.to_singular(type(getattr(sub_resource,
                                                             resource + 's')).__name__)) and \
                hasattr(getattr(brokers, self.to_singular(type(getattr(sub_resource,
                                                                     resource + 's')).__name__)),
                        method):
                    method_ref = getattr(getattr(brokers,
                                                 self.to_singular(type(getattr(sub_resource,
                                                                             resource + 's')).__name__)),
                                         method)

            if not method_ref:
                self.error('cannot find any context for type "%s"' % resource)

        elif isinstance(resource, brokers.Base):
            if hasattr(resource, method):
                method_ref = getattr(resource, method)
            elif hasattr(brokers, type(resource).__name__ + 's') and \
            hasattr(getattr(brokers, type(resource).__name__ + 's'), method):
                method_ref = getattr(getattr(brokers, type(resource).__name__ + 's'), method)

        if method_ref and method_ref.__doc__:
            doc = method_ref.__doc__
            params_arr = doc.split('\n')
            params_list = []
#            params_hash = {}

            for var in params_arr:
                if '' != var and var.find(PARAM_ANNOTATION) != -1:
                    splitted_line = var.strip().split(' ')
                    if len(splitted_line) >= 2:
                        prefix = splitted_line[0].replace((PARAM_ANNOTATION + ' '),
                                                          '--').replace(PARAM_ANNOTATION, '--')
                        param = splitted_line[1].replace('**', '')

                        if len(splitted_line) > 3 and splitted_line[3].startswith('('):
                            typ = ''.join(splitted_line[2:3])
                            if prefix.startswith('['):
                                typ = typ + ']'
                        else:
                            typ = ''.join(splitted_line[2:])

                        if param.find('.') != -1:
                            splitted_param = param.split('.')
                            new_param = '_'.join(splitted_param[1:])
                            if new_param.find('id|name') != -1:
                                param = new_param.replace('_id|name', '')
                            else:
                                param = new_param

#                        params_hash[param.replace(':', '')] = splitted_line[1].replace(':', '') \
#                                                                              .replace('id|name', 'name')
                        params_list.append(prefix + param + ' ' + typ)
        return params_list

    def is_supported_type(self, types, typ):
        if typ not in types:
            self.error('not supported type "%s"' % typ)
            return False
        return True
