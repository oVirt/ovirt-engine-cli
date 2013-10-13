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


from cli import compat


class Warning(Exception):  # @ReservedAssignment
    """Base class for python-cli warnings."""

    def __init__(self, message=None, **kwargs):
        if message is None: message = self.__doc__
        message = message + '\n' if not message.endswith('\n') \
                                 else message
        compat.super(Warning, self).__init__(message)

        for key in kwargs:
            setattr(self, key, kwargs[key])

class GenericWarning(Warning):
    """Generic warning."""

