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


import inspect
from ovirtsdk.utils.ordereddict import OrderedDict

class MethodHelper():

    NON_ARG_TEMPLATE = ':not-arg'

    @staticmethod
    def getMethodArgs(module, cls, method, get_varargs=False, get_keywords=False, drop_self=False, exclude=['context']):
        '''Returns list of method's arguments'''
        if hasattr(module, cls):
            cls_ref = getattr(module, cls)
            if cls_ref and hasattr(cls_ref, method):
                method_ref = getattr(cls_ref, method)
                if method_ref:
                    try:
                        res = getattr(inspect.getargspec(method_ref), 'args')
                        for item in exclude:
                            if(res.__contains__(item)):
                                res.remove(item)
                        if not res: res = []
                        if drop_self and res.__contains__('self'):
                            res.remove('self')
                        if get_varargs:
                            varargs_res = getattr(inspect.getargspec(method_ref), 'varargs')
                            if varargs_res: res.append(varargs_res)
                        if get_keywords:
                            keywords_res = getattr(inspect.getargspec(method_ref), 'keywords')
                            if keywords_res: res.append(keywords_res)
                        return res
                    except:
                        pass
        return []

    @staticmethod
    def get_method_params(module, clazz, method, holder=OrderedDict(), expendNestedTypes=False, groupOptions=False):
        args = MethodHelper.getMethodArgs(module, clazz, method)
        expender = MethodHelper.__expend_nested_type

        if not groupOptions:
            if args:
                if len(args) == 3:
                    if expendNestedTypes:
                        cand = expender(args[1], module, method, [])
                    else:
                        cand = args[1]

                    cand = ", ".join(cand) if type(cand) == list else cand

                    if not holder.has_key(args[2]):
                        holder[args[2]] = cand
                    else:
                        if holder[args[2]] == None:
                            if args[1] != None:
                                holder[args[2]] = 'None, ' + cand
                        else:
                            holder[args[2]] = holder[args[2]] + ', ' + cand
                elif len(args) == 2:
                    if not holder.has_key(args[1]):
                        holder[args[1]] = None
                    else:
                        if holder[args[1]] == None:
                            if holder[args[1]] != None:
                                holder[args[1]] = 'None' + ', ' + holder[args[1]]
                        else:
                            holder[args[1]] = holder[args[1]] + ', ' + 'None'
            return MethodHelper.__remove_replications(holder)
        else:
            if args:
                if len(args) == 3:
                    if expendNestedTypes:
                        cand = expender(args[1], module, method, [])
                    else:
                        cand = args[1]
                    cand = cand if type(cand) == list else [cand]

                    if not holder.has_key(args[2]):
                        holder[args[2]] = [cand]
                    else:
                        if holder[args[2]] == None:
                            if args[1] != None:
                                holder[args[2]] = [[], cand]
                        elif cand not in holder[args[2]]:
                            holder[args[2]].append(cand)
                elif len(args) == 2:
                    if not holder.has_key(args[1]):
                        holder[args[1]] = [[]]
                    else:
                        if holder[args[1]] == None:
                            if holder[args[1]] != None:
                                holder[args[1]] = [[], holder[args[1]]]
                        elif [] not in holder[args[1]]:
                            holder[args[1]].append([])

    @staticmethod
    def __remove_replications(holder):
        for k, v in holder.items():
            if v:
                new_val = []
                for item in v.split(', '):
                    if item and item not in new_val:
                        new_val.append(item)
                holder[k] = ", ".join(sorted(new_val))

    @staticmethod
    def __expend_nested_type(type_name, module, method, expended_types):
        """Recursive method's args types resolution"""
        getMethodArgs = MethodHelper.getMethodArgs
        expend_nested_type = MethodHelper.__expend_nested_type

        from ovirtcli.utils.typehelper import TypeHelper
        typ = TypeHelper.getDecoratorType(type_name)

        if typ:
            expended_types_tmp = getMethodArgs(module, typ, method, drop_self=True)
            if len(expended_types_tmp) > 1:
                for item in expended_types_tmp:
                    if item != type_name:
                        expend_nested_type(item, module, method, expended_types)
            elif len(expended_types_tmp) > 0:
                expended_types.append(expended_types_tmp[0])
        else:
            expended_types.append(type_name)
        return expended_types

    @staticmethod
    def get_documented_arguments(method_ref, as_params_collection=False, spilt_or=False):
        """Return a list of documented arguments for specific method, ignoring metadata."""
        return MethodHelper.get_arguments_documentation(method_ref, as_params_collection, spilt_or, ignore_non_args=True)


    @staticmethod
    def get_arguments_documentation(method_ref, as_params_collection=False, spilt_or=False, ignore_non_args=False):
        """Return a list of documented arguments with arguments metadata for specific method."""

        PARAM_ANNOTATION = '@param'
        IVAR_ANNOTATION = '@ivar'
        params_list = []
        ivars_list = []
        PERIOD_SYMBOL = '-'

        if method_ref and method_ref.__doc__:
            doc = method_ref.__doc__
            params_arr = doc.split('\n')

            for var in params_arr:
                if not ignore_non_args and var.find('Overload') != -1:
                    params_list.append('\n' + var.strip() + MethodHelper.NON_ARG_TEMPLATE + '\n')
                elif '' != var and var.find(PARAM_ANNOTATION) != -1:
                    splitted_line = var.strip().split(' ')
                    if len(splitted_line) >= 2:
                        prefix = splitted_line[0].replace((PARAM_ANNOTATION + ' '),
                                                          '--').replace(PARAM_ANNOTATION, '--')
                        param = splitted_line[1].replace('**', '')

                        if len(splitted_line) > 3 and splitted_line[3].startswith('('):
                            typ = ' '.join(splitted_line[2:3])
                            if prefix.startswith('['):
                                typ = typ + ']'
                        else:
                            typ = ' '.join(splitted_line[2:])

                        if param.find('.') != -1:
                            splitted_param = param.split('.')
                            new_param = PERIOD_SYMBOL.join(splitted_param[1:])
                            param = new_param

#                        params_hash[param.replace(':', '')] = splitted_line[1].replace(':', '') \
#                                                                              .replace('id|name', 'name')
                        if as_params_collection:
                            if spilt_or and param.find('|') != -1:
                                spl = param.replace(':', '').split('|')
                                if len(spl) == 2:
                                    p1 = spl[0]
                                    if spl[0].find(PERIOD_SYMBOL) != -1 :
                                        spl_ = spl[0].split('-')
                                        p2 = '-'.join(spl_[:len(spl_) - 1]) + '-' + spl[1]
                                    else:
                                        p2 = spl[1]

                                    params_list.append(p1)
                                    params_list.append(p2)
                                else:
                                    params_list.append(param.replace(':', ''))
                            else:
                                params_list.append(param.replace(':', ''))
                        else:
                            if spilt_or and param.find('|') != -1:
                                spl = param.split('|')
                                if len(spl) == 2:
                                    p1 = spl[0]
                                    if spl[0].find(PERIOD_SYMBOL) != -1 :
                                        spl_ = spl[0].split('-')
                                        p2 = '-'.join(spl_[:len(spl_) - 1]) + '-' + spl[1]
                                    else:
                                        p2 = spl[1]

                                    params_list.append(prefix + p1 + ' ' + typ)
                                    params_list.append(prefix + p2 + ' ' + typ)
                                else:
                                    params_list.append(prefix + param + ' ' + typ)
                            else:
                                params_list.append(prefix + param + ' ' + typ)
                if params_list and params_list[-1].find('collection') != -1:
                    params_list.append('  {' + MethodHelper.NON_ARG_TEMPLATE)
                elif not ignore_non_args and '' != var and var.find(IVAR_ANNOTATION) != -1:
                    params_list.append('    ' + var.lstrip().replace(IVAR_ANNOTATION + ' ', '') + MethodHelper.NON_ARG_TEMPLATE)
                elif not ignore_non_args and '' != var and var.find('}') != -1:
                    params_list.append('  }' + MethodHelper.NON_ARG_TEMPLATE)

        return params_list

    @staticmethod
    def get_object_methods(obj, exceptions=[]):
        """Return a list of type actions."""
        actions = []

        dct = (obj if type(obj) == type else type(obj)).__dict__
        if dct and len(dct) > 0:
            for method in dct:
                if method not in exceptions and not method.startswith('_'):
                    actions.append(method)
        return actions
