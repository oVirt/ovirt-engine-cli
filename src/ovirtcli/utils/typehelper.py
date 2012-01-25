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
        if TypeHelper.__known_decorators_types == None:
            TypeHelper.__known_decorators_types = TypeHelper._getKnownDecoratorsTypes()
        if TypeHelper.__known_decorators_types.has_key(name.lower()):
            return TypeHelper.__known_decorators_types[name.lower()]
        return None
