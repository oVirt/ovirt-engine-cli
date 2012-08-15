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

import types

class MultiValueDict(dict):
    '''
    Dictionary that supports multi-value based keys
    '''

    def __init__(self, *args, **kwargs):
        if args and args[0] and args[0][0] and type(args[0][0]) == types.TupleType:
            for item in args[0]:
                if len(item) >= 2:
                    self.__setitem__(item[0], item[1])
                elif len(item) == 1:
                    self.__setitem__(item[0], None)
        else:
            dict.__init__(self, *args, **kwargs)

    def __setitem__(self, key, value):
        if self.has_key(key):
            if self[key] <> None and type(self[key]) != types.ListType:
                tmp = self[key]
                super(MultiValueDict, self).__setitem__(key, [])
                self[key].append(tmp)
                self[key].append(value)
            elif self[key] == None:
                super(MultiValueDict, self).__setitem__(key, value)
            else:
                self[key].append(value)
        else:
            super(MultiValueDict, self).__setitem__(key, value)
