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

from ovirtsdk.xml import params
from ovirtsdk.infrastructure import brokers
from ovirtcli.utils.methodhelper import MethodHelper

class TypeHelper():
    __known_wrapper_types = None
    __known_decorators_types = None

    @staticmethod
    def _getKnownTypes():
        known_wrapper_types = {}
        for name, obj in inspect.getmembers(params):
            if inspect.isclass(obj) and (isinstance(obj, type(params.BaseResource)) or
                                         isinstance(obj, type(params.BaseResources)) or
                                         isinstance(obj, type(params.GeneratedsSuper)) or
                                         isinstance(obj, type(params.BaseDevices)) or
                                         isinstance(obj, type(params.BaseDevice))):
                known_wrapper_types[name.lower()] = name
        return known_wrapper_types

    @staticmethod
    def _getKnownDecoratorsTypes():
        __known_decorators_types = {}
        for name, obj in inspect.getmembers(brokers):
            if inspect.isclass(obj):
                __known_decorators_types[name.lower()] = name
        return __known_decorators_types

    @staticmethod
    def isKnownType(typ):
        if TypeHelper.__known_wrapper_types == None:
            TypeHelper.__known_wrapper_types = TypeHelper._getKnownTypes()
        return TypeHelper.__known_wrapper_types.has_key(typ.lower())

    @staticmethod
    def isKnownDecoratorType(typ):
        if TypeHelper.__known_decorators_types == None:
            TypeHelper.__known_decorators_types = TypeHelper._getKnownDecoratorsTypes()
        return TypeHelper.__known_decorators_types.has_key(typ.lower())

    @staticmethod
    def getKnownTypes():
        if TypeHelper.__known_wrapper_types == None:
            TypeHelper.__known_wrapper_types = TypeHelper._getKnownTypes()
        return TypeHelper.__known_wrapper_types.values()

    @staticmethod
    def getKnownDecoratorsTypes():
        if TypeHelper.__known_decorators_types == None:
            TypeHelper.__known_decorators_types = TypeHelper._getKnownDecoratorsTypes()
        return TypeHelper.__known_decorators_types.values()

    @staticmethod
    def getDecoratorType(name):
        if name and name != '':
            if TypeHelper.__known_decorators_types == None:
                TypeHelper.__known_decorators_types = TypeHelper._getKnownDecoratorsTypes()
            if TypeHelper.__known_decorators_types.has_key(name.lower()):
                return TypeHelper.__known_decorators_types[name.lower()]
        return None

    @staticmethod
    def get_actionable_types(expendNestedTypes=False, groupOptions=False):
        """INTERNAL: return a list of actionable types."""
        types = {}
        exceptions = ['delete', 'update']

        for decorator in TypeHelper.getKnownDecoratorsTypes():
                if not decorator.endswith('s'):
                    dct = getattr(brokers, decorator).__dict__
                    if dct and len(dct) > 0:
                        for method in dct:
                            if method not in exceptions and not method.startswith('_'):
                                MethodHelper.get_method_params(brokers, decorator, '__init__', types,
                                                               expendNestedTypes=expendNestedTypes,
                                                               groupOptions=groupOptions)
                                break
        return types

    @staticmethod
    def get_types_containing_method(method, expendNestedTypes=False, groupOptions=False):
        """return a list of types by method including context in which this method available."""
        types = {}

        for decorator in TypeHelper.getKnownDecoratorsTypes():
                if not decorator.endswith('s'):
                    dct = getattr(brokers, decorator).__dict__
                    if dct and len(dct) > 0 and dct.has_key(method):
                        MethodHelper.get_method_params(brokers, decorator, '__init__', types,
                                                       expendNestedTypes=expendNestedTypes,
                                                       groupOptions=groupOptions)
        return types

    @staticmethod
    def get_types_by_method(plural, method, expendNestedTypes=False, groupOptions=False):
        """INTERNAL: return a list of types that implement given method and context/s of this types."""
        sing_types = {}

        if method:
            for decorator in TypeHelper.getKnownDecoratorsTypes():
                dct = getattr(brokers, decorator).__dict__
                if dct.has_key(method):
                    if decorator.endswith('s'):
                        cls_name = TypeHelper.getDecoratorType(TypeHelper.to_singular(decorator))
                        if cls_name:
                            MethodHelper.get_method_params(brokers,
                                                           cls_name,
                                                           '__init__',
                                                           sing_types,
                                                           expendNestedTypes,
                                                           groupOptions)

            if plural:
                sing_types_plural = {}
                for k in sing_types.keys():
                    sing_types_plural[TypeHelper.to_plural(k)] = sing_types[k]
                return sing_types_plural
            return sing_types

    @staticmethod
    def to_singular(string):
        if string.endswith("ies"):
            return string[:-3] + "y"
        if string.endswith("s"):
            return string[:-1]
        return string

    @staticmethod
    def to_plural(string):
        if string.endswith("y"):
            return string[:-1] + "ies"
        if not string.endswith("s"):
            return string + "s"
        return string
