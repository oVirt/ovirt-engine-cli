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


from cli.command import Command
from ovirtcli.utils.typehelper import TypeHelper

from ovirtsdk.xml import params
from ovirtsdk.utils.parsehelper import ParseHelper
import uuid
from ovirtcli.utils.methodhelper import MethodHelper
from ovirtsdk.infrastructure import brokers
from ovirtsdk.utils.ordereddict import OrderedDict
import itertools
from cli.messages import Messages
import types
import re
import keyword
import __builtin__


class OvirtCommand(Command):
    """Base class for oVirt commands."""

    def check_connection(self):
        """ensure we have a connection."""
        if self.context.connection is None:
            self.error('not connected', help='try \'help connect\'')
        return self.context.connection

    def resolve_base(self, options):
        """resolves a base object from a set of '--type-identifier value' options."""
        collection_candidate = self.check_connection()
        parnet_candidate_locator = 0
        base = None

        parnet_candidates = [key for key in options.keys() if key.endswith('-identifier')]
        parnet_candidates_permutations = list(itertools.permutations(parnet_candidates))

        if parnet_candidates_permutations[0]:
            for combination in parnet_candidates_permutations:
                for item in combination:
                    key = item
                    val = options[key]
                    parnet_candidate_locator += 1
                    typename = key[2:-11]

                    coll = typename + 's'
                    if not (TypeHelper.isKnownType(typename) or  TypeHelper.isKnownType(coll)):
                        self.error(Messages.Error.NO_SUCH_TYPE % typename)

                    if hasattr(collection_candidate, coll):
                        coll_ins = getattr(collection_candidate, coll)
                        if hasattr(coll_ins, 'get'):
                            if not val:
                                self.error(Messages.Error.INVALID_OPTION % key)
                            uuid_cand = self._toUUID(val)
                            if uuid_cand != None:
                                base = coll_ins.get(id=val)
                            else:
                                base = coll_ins.get(name=val)

                            if not base:
                                if len(combination) > parnet_candidate_locator:
                                    continue
                                else:
                                    self.error(Messages.Error.NO_SUCH_OBJECT % (typename, val))

                    if len(parnet_candidates) == parnet_candidate_locator:
                        return base
                    else:
                        collection_candidate = base

            self.error(Messages.Error.CANNOT_CONSTRUCT_COLLECTION_MEMBER_VIEW % str(parnet_candidates_permutations))

    def __try_parse(self, param):
        """INTERNAL: try parsing data to int"""
        try:
            if param and param[0] in ('-', '+') and param[1:].isdigit():
                return int(param)
            elif param and param.isdigit():
                return int(param)
            else: return param
        except:
            return param

    def __do_set_primitive_list_data(self, obj, prop, val):
        for param in self.__split_with_escape(str(val), delimiter=','):
            getattr(obj, prop).append(param)

    def __do_set_data(self, obj, prop, fq_prop, val):
        """INTERNAL: set data in to object based on 'prop' map segmentation"""
        props = prop.split('-')
        props_len = len(props)
        if props_len > 1 or (props_len == 1 and hasattr(obj, prop)):
            for i in range(props_len):
                if props[i] == 'type': props[i] = 'type_'
                if i == (props_len - 1) and hasattr(obj, props[i]) and type(getattr(obj, props[i])) != list:
                    self.__set_property(obj, props[i], val, fq_prop)
                    return
                if hasattr(obj, props[i]) and type(getattr(obj, props[i])) == list:
                        params_set_cand = ParseHelper.getXmlType(props[i])
                        if params_set_cand:
                            obj_params_set_cand = params_set_cand.factory()
                            root_obj_params_set_cand = obj_params_set_cand
                        else:
                            self.__do_set_primitive_list_data(obj, props[i], val)
                            return

                        if not val:
                            self.error(Messages.Error.INVALID_COLLECTION_BASED_OPTION_SYNTAX % prop)

                        for param in self.__split_with_escape(str(val), delimiter=','):
                            obj_params_set_cand = root_obj_params_set_cand
                            if not param.startswith(props[i] + '.'):
                                self.error(
                                       Messages.Error.INVALID_OPTION_SEGMENT % \
                                       (param, prop)
                                )
                            param_data = param.replace(props[i] + '.', '').split('=')
                            if len(param_data) == 2:
                                spplited_param_data = param_data[0].split('.')
                                for param_period in spplited_param_data:
                                    if spplited_param_data[-1] == param_period:
                                        if not hasattr(obj_params_set_cand, param_period):
                                            param_period = self.fixParamNameIfParamIsKeyword(param_period)
                                        if hasattr(obj_params_set_cand, param_period):
                                            if getattr(obj_params_set_cand, param_period) != None:
                                                getattr(obj, props[i]).append(obj_params_set_cand)
                                                obj_params_set_cand = params_set_cand.factory()
                                                root_obj_params_set_cand = obj_params_set_cand
                                            setattr(obj_params_set_cand, param_period,
                                                    self.__try_parse(param_data[1].strip()))
                                        else:
                                            self.error(Messages.Error.INVALID_OPTION_SEGMENT % \
                                                       (param_period, param))
                                    elif hasattr(obj_params_set_cand, param_period) and \
                                         getattr(obj_params_set_cand, param_period) == None:
                                        param_period_cand = ParseHelper.getXmlType(param_period)
                                        if param_period_cand:
                                            param_period_cand_obj = param_period_cand.factory()
                                            setattr(obj_params_set_cand, param_period, param_period_cand_obj)
                                            obj_params_set_cand = param_period_cand_obj
                                    elif hasattr(obj_params_set_cand, param_period):
                                        param_period_cand = ParseHelper.getXmlType(param_period)
                                        if param_period_cand:
                                            param_period_cand_obj = getattr(obj_params_set_cand, param_period)
                                            obj_params_set_cand = param_period_cand_obj
                                    else:
                                        self.error(Messages.Error.INVALID_OPTION_SEGMENT % \
                                                   (param_period, param))
                            else:
                                self.error(Messages.Error.INVALID_COLLECTION_BASED_OPTION_SYNTAX % prop)
                        getattr(obj, props[i]).append(obj_params_set_cand)
                elif hasattr(obj, props[i]):
                    content = getattr(obj, props[i])
                    if content is None:
                        cand1 = ParseHelper.getXmlType(props[i])
                        if cand1:
                            cand = cand1.factory()
                            setattr(obj, props[i], cand)
                            obj = cand
                    else:
                        obj = content
                else:
                    cand2 = ParseHelper.getXmlTypeInstance(props[i])
                    if cand2 and hasattr(obj, cand2):
                        cand1 = ParseHelper.getXmlType(cand2)
                        if cand1:
                            props[i] = cand2
                            cand = cand1.factory()
                            setattr(obj, props[i], cand)
                            obj = cand
                        else:
                            self.error(Messages.Error.NO_SUCH_TYPE % cand2)
                    else:
                        self.error(Messages.Error.INVALID_ARGUMENT_SEGMENT % props[i])
        else:
            self.__set_property(obj, prop, val, fq_prop)

    def fixParamNameIfParamIsKeyword(self, param):
        if param in dir(__builtin__) or keyword.iskeyword(param):
            return param + '_'
        return param

    def __set_property(self, obj, prop, val, fq_prop):
        """INTERNAL: set data in to property"""
        if hasattr(obj, prop):
            setattr(obj, prop, val)
        elif hasattr(obj, prop + '_'):
            setattr(obj, prop + '_', val)
        else:
            pass
#            self.error('%s is not valid argument.' % fq_prop)

    def update_object_data(self, obj, options, scope=None):
        """Updates object properties with values from `options'."""

        for key in options.keys():
            prop = key.replace('--', '')
            val = options[key]
            if not prop.endswith('-id') and prop.endswith('-identifier'): continue
            if type(val) == types.ListType:
                for item in val:
                    self.__do_set_data(obj=obj, prop=prop, fq_prop=key, val=item)
            else:
                self.__do_set_data(obj=obj, prop=prop, fq_prop=key, val=val)

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


    def _get_query_params(self, opts, query_arg='--query', kwargs_arg='--kwargs'):
        """INTERNAL: retrieves query and kwargs from attribute options"""
        query = opts[query_arg] if opts.has_key(query_arg) else None
        kw = {}
        empty = True
        if opts.has_key(kwargs_arg):
            if opts[kwargs_arg]:
                for item in opts[kwargs_arg].split(';'):
                    if item.find("=") != -1:
                        k, v = item.split('=')
                        kw[k.replace('-', '.')] = v
                        empty = False
                    elif empty:
                        self.error(Messages.Error.INVALID_KWARGS_FORMAT % item)
            else:
                self.error(Messages.Error.INVALID_KWARGS_CONTENT)
        mopts = {}
        for k, v in opts.iteritems():
            if k != query_arg and k != kwargs_arg and not k.endswith('-identifier'):
                mopts[k if not k.startswith('--') else k[2:]] = v
        kw.update(mopts)

        return query, kw


    def get_collection(self, typ, opts={}, base=None, context_variants=[]):
        """retrieves collection members"""
        self.check_connection()
        connection = self.context.connection
        query, kwargs = self._get_query_params(opts)

        if base is None:
            if hasattr(connection, typ):
                options = self.get_options(method='list', resource=TypeHelper.to_singular(typ), as_params_collection=True)

                if query and 'query' not in options:
                    self.error(Messages.Error.NO_QUERY_ARGS)
                if kwargs and 'kwargs' not in options:
                    self.error(Messages.Error.NO_KWARGS % 'list')

                if query and kwargs:
                    return getattr(connection, typ).list(query=query, **kwargs)
                if query:
                    return getattr(connection, typ).list(query=query)
                if kwargs:
                    return getattr(connection, typ).list(**kwargs)
                return getattr(connection, typ).list()
        else:
            if hasattr(base, typ):
                options = self.get_options(method='list', resource=getattr(base, typ), as_params_collection=True)

                if query and 'query' not in options:
                    self.error(Messages.Error.NO_QUERY_ARGS)
                if kwargs and 'kwargs' not in options:
                    self.error(Messages.Error.NO_KWARGS % 'list')

                if query and kwargs:
                    return getattr(base, typ).list(query=query, **kwargs)
                if query:
                    return getattr(base, typ).list(query=query)
                if kwargs:
                    return getattr(base, typ).list(**kwargs)
                return getattr(base, typ).list()

        err_str = Messages.Error.NO_SUCH_COLLECTION
        if context_variants:
            err_str = err_str + (Messages.Info.POSSIBALE_ARGUMENTS_COMBINATIONS %
                                 str(context_variants))
        self.error(err_str % typ)

    def validate_options(self, opts, options):
        for opt in opts.keys():
            if opt.startswith('--'):
                opt_item = opt[2:]
            else: opt_item = opt
            if opt_item not in options and not opt_item.endswith('-identifier'):
                self.error(Messages.Error.NO_SUCH_OPTION % opt)

    def get_object(self, typ, obj_id, base=None, opts={}, context_variants=[]):
        """Return an object by id or name."""
        self.check_connection()
        connection = self.context.connection
        name, kwargs = self._get_query_params(opts, query_arg='--name')

        candidate = typ if typ is not None and isinstance(typ, type('')) \
                        else type(typ).__name__.lower()

        if base:
            options = self.get_options(method='get', resource=base,
                                       as_params_collection=True,
                                       context_variants=context_variants)
        else:
            options = self.get_options(method='get', resource=typ,
                                       as_params_collection=True,
                                       context_variants=context_variants)
            base = connection

        self.validate_options(opts, options)

        if name and 'name' not in options:
            self.error(Messages.Error.NO_NAME)
        if kwargs and kwargs.has_key('id') and 'id' not in options:
            self.error(Messages.Error.NO_ID % 'show')

        if hasattr(base, candidate + 's'):
            coll = getattr(base, candidate + 's')
            if coll is not None:
                if name:
                    return self.__get_by_name(coll, name, kwargs)
                if kwargs and kwargs.has_key('id'):
                    id, kwargs = self._get_query_params(opts, query_arg='--id')
                    return self.__get_by_id(coll, str(id), kwargs)
                else:
                    identifier = self.__produce_identifier(obj_id)
                    if identifier:
                        return self.__get_by_id(coll, str(obj_id), kwargs)
                    else:
                        return self.__get_by_name(coll, obj_id, kwargs)
        else:
            err_str = Messages.Error.NO_SUCH_TYPE_OR_ARS_NOT_VALID
            if context_variants:
                err_str = err_str + (Messages.Info.POSSIBALE_ARGUMENTS_COMBINATIONS
                                      % str(context_variants))
            self.error(err_str % candidate)

        return None

    def __get_by_name(self, coll, name, kwargs):
        if kwargs:
            return coll.get(name=name, **kwargs)
        else:
            return coll.get(name=name)

    def __get_by_id(self, coll, id, kwargs):
        if kwargs:
            return coll.get(id=id, **kwargs)
        else:
            return coll.get(id=id)

    def __produce_identifier(self, candidate):
        if type(candidate) == str:
            match = re.search(r'[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}', candidate)
            if match:
                return self._toUUID(candidate)
            match = re.search(r'[-+]?\d+', candidate)
            if match:
                return self._toLong(candidate)
        elif type(candidate) == int or type(candidate) == long:
            return candidate
        return None

    def _toLong(self, string):
        try:
            return long(string)
        except:
            return None

    def _toUUID(self, string):
        try:
            return uuid.UUID(string)
        except:
            return None

    def get_singular_types(self, method, typ=None, expendNestedTypes=True, groupOptions=True):
        """Return a list of singular types."""
        typs = TypeHelper.get_types_by_method(False, method, expendNestedTypes, groupOptions)
        if typ:
            if typs.has_key(typ):
                return typs[typ]
            else: return []
        else:
            return typs

    def get_plural_types(self, method, typ=None, expendNestedTypes=True, groupOptions=True):
        """Return a list of plural types."""
        typs = TypeHelper.get_types_by_method(True, method, expendNestedTypes, groupOptions)
        if typ:
            if typs.has_key(typ):
                return typs[typ]
            else: return []
        else:
            return typs

    def get_options(self, method, resource, sub_resource=None, as_params_collection=False, context_variants=[]):
        """Return a list of options for typ/action."""

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
                hasattr(brokers, TypeHelper.to_singular(type(getattr(sub_resource,
                                                             resource + 's')).__name__)) and \
                hasattr(getattr(brokers, TypeHelper.to_singular(type(getattr(sub_resource,
                                                                     resource + 's')).__name__)),
                        method):
                    method_ref = getattr(getattr(brokers,
                                                 TypeHelper.to_singular(type(getattr(sub_resource,
                                                                             resource + 's')).__name__)),
                                         method)

            if not method_ref:
                err_str = Messages.Error.NO_SUCH_CONTEXT
                if context_variants:
                    err_str = err_str + (Messages.Info.POSSIBALE_ARGUMENTS_COMBINATIONS
                                         % str(context_variants))
                self.error(err_str % resource)

        elif isinstance(resource, brokers.Base):
            if hasattr(resource, method):
                method_ref = getattr(resource, method)
            elif hasattr(brokers, type(resource).__name__ + 's') and \
            hasattr(getattr(brokers, type(resource).__name__ + 's'), method):
                method_ref = getattr(getattr(brokers, type(resource).__name__ + 's'), method)

        return MethodHelper.get_arguments_documentation(method_ref, as_params_collection)

    def is_supported_type(self, types, typ):
        if typ not in types:
            self.error(Messages.Error.NO_SUCH_TYPE % typ)
            return False
        return True

    def execute_method(self, resource, method_name, opts={}):
        """executes given method with specified opts."""

        if hasattr(resource, method_name):
            method = getattr(resource, method_name)

            method_args = OrderedDict().fromkeys(MethodHelper.getMethodArgs(brokers,
                                                                            method.im_class.__name__,
                                                                            method_name,
                                                                            drop_self=True))

            if method_args:
                for arg in method_args.keys():
                    param_type = ParseHelper.getXmlType(arg)
                    if param_type:
                        method_args[arg] = self.update_object_data(param_type.factory(), opts)
                    elif opts.has_key('--' + arg):
                        method_args[arg] = opts['--' + arg]
                    else:
                        # TODO: throw error if param is mandatory
                        pass

                try:
                    result = method(**method_args)
                except AttributeError:
                    self.error(Messages.Error.UNSUPPORTED_ATTRIBUTE)
            else:
                result = method()
            return result
        else:
            self.error('no such action "%s"' % method_name)

    def _get_action_methods(self, obj):
        """INTERNAL: return a list of type actions."""

        return MethodHelper.get_object_methods(obj, exceptions=['delete', 'update'])

    def __split_with_escape(self, text, delimiter=',', escape='\\'):
        """
        Splits a string so that the delimiter is ignored if it is preceded by
        the escape character.
        """

        chunks = []
        chunk = ''
        escaping = False
        for c in list(text) + [None]:
            if not escaping:
                if c is None:
                    chunks.append(chunk)
                    chunk = ''
                    escaping = False
                elif c == escape:
                    escaping = True
                elif c == delimiter:
                    chunks.append(chunk)
                    chunk = ''
                    escaping = False
                else:
                    chunk += c
                    escaping = False
            else:
                if c is None:
                    chunk += escape
                    chunks.append(chunk)
                    chunk = ''
                    escaping = False
                elif c == escape:
                    chunk += escape
                    escaping = False
                elif c == delimiter:
                    chunk += c
                    escaping = False
                else:
                    chunk += escape
                    chunk += c
                    escaping = False
        return chunks
