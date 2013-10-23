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

class Singleton(type):
    """
    The singleton annotation

    applying this annotation on class, will make sure that no
    more than single instance of this class can be created.
    """
    __all_instances = {}
    def __call__(cls, *args, **kwargs):  # @NoSelf
        if cls not in cls.__all_instances:
            cls.__all_instances[cls] = super(
                         Singleton,
                         cls).__call__(
                               *args,
                               **kwargs
                         )
        return cls.__all_instances[cls]
