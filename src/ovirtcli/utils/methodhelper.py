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

class MethodHelper():
    @staticmethod
    def getMethodArgs(module, cls, method, get_varargs=False, get_keywords=False, drop_self=False):
        '''Returns list of method's arguments'''
        if hasattr(module, cls):
            cls_ref = getattr(module, cls)
            if cls_ref and hasattr(cls_ref, method):
                method_ref = getattr(cls_ref, method)
                if method_ref:
                    try:
                        res = getattr(inspect.getargspec(method_ref), 'args')
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
    def get_method_params(module, clazz, method, holder={}):
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

    @staticmethod
    def get_documented_arguments(method_ref, as_params_collection=False, spilt_or=False):
        """Return a list of arguments documented for specific method."""

        PARAM_ANNOTATION = '@param'
        params_list = []
        PERIOD_SYMBOL = '-'

        if method_ref and method_ref.__doc__:
            doc = method_ref.__doc__
            params_arr = doc.split('\n')

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

        return params_list
