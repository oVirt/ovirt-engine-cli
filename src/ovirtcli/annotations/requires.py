#
# Copyright (c) 2013 Red Hat, Inc.
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

import types


class Requires(object):
    """
    Checks that method arg is of a given type

    @note:

    1. checks that method's argument of type DFSAEvent

        @Requires(DFSAEvent)
        def method1(self, event):
            ...

    2. checks that method's argument is a List of DFSAEvent

        @Requires([DFSAEvent])
        def method2(self, events):
            ...
    """

    def __init__(self, types_to_check):
        """
        Checks that method arg is of a given type

        @param types_to_check: the types to validate against
        @note:

        1. checks that method's argument of type DFSAEvent

            @Requires(DFSAEvent)
            def method1(self, event):
                ...

        2. checks that method's argument is a List of DFSAEvent

            @Requires([DFSAEvent])
            def method2(self, events):
                ...
        """
        assert types_to_check != None
        self.__types_to_check = types_to_check

    def __call__(self, original_func):
        decorator_self = self
        def wrappee(*args, **kwargs):
            self.__check_list(
                      args[1:],
                      decorator_self.__types_to_check
            )
            return original_func(*args, **kwargs)
        return wrappee

    def __raise_error(self, typ):
        raise TypeError(
                "%s instance is expected."
                %
                typ.__name__
        )

    def __check_list(self, candidates, typs):
        if isinstance(typs, types.ListType):
            if type(candidates[0]) is types.ListType:
                # the list of items of a specific type
                if candidates[0]:
                    for candidate in candidates[0]:
                        if not isinstance(candidate, typs[0]):
                            self.__raise_error(typs[0])
                else:
                    self.__raise_error(types.ListType)
        else:
            # the items is of a specific type
            if not isinstance(candidates[0], typs):
                self.__raise_error(typs)
