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
import types

from ovirtcli.annotations.requires import Requires
from ovirtcli.state.dfsastate import DFSAState

class Error(Exception):
    """Base class for python-cli errors."""

    def __init__(self, message=None, **kwargs):
        if message is None:
            message = self.__doc__
        message = message + '\n' if not message.endswith('\n') \
                                 else message
        compat.super(Error, self).__init__(message)
        for key in kwargs:
            setattr(self, key, kwargs[key])


class ParseError(Error):
    """Error parsing command line."""


class CommandError(Error):
    """Illegal command."""

class SyntaxError(Error):  # @ReservedAssignment
    """Illegal syntax."""

class StateError(Error):
    """raised when state change error occurs."""
#     @Requires([DFSAEvent, types.StringType])
    def __init__(self, destination, current):
        """
        @param destination: the destination DFSAEvent
        @param current: the current state
        """
        super(StateError, self).__init__(
             message=
             (
                '\n\nMoving to the "%s" state is not allowed,\n'
                %
                str(DFSAState(destination.get_destination()))
             )
             +
             (
                'eligible states from the "%s" state are:\n%s'
                %
                (
                    str(DFSAState(current)),
                    str([ str(DFSAState(src))
                      for src in destination.get_sources()
                      ]
                    )
                 )
             )
        )

class UnknownEventError(Error):
    """raised when unregistered event is triggered."""
#     @Requires(types.StringType)
    def __init__(self, name):
        """
        @param name: the name of DFSAEvent
        """
        super(UnknownEventError, self).__init__(
             message=(
                'Event %s, was not properly registered.' % \
                name
             )
        )
