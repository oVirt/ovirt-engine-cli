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


_super = super

def super(type, self):
    if issubclass(type, object):
        return _super(type, self)
    class proxy(object):
        def __init__(self, type, obj):
            object.__setattr__(self, '__type__', type)
            object.__setattr__(self, '__obj__', obj)
        def __getattribute__(self, name):
            def bind(func, self):
                def _f(*args):
                    func(self, *args)
                return _f
            type = object.__getattribute__(self, '__type__')
            obj = object.__getattribute__(self, '__obj__')
            return bind(getattr(type, name), obj)
    base = type.__bases__[0]
    return proxy(base, self)
