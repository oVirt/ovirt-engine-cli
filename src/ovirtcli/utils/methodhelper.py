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
