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
#


from ovirtcli.state.dfsastate import DFSAState
from ovirtcli.annotations.requires import Requires
import types

class DFSAEvent(object):
    '''
    Finite-State Automata event
    '''

    def __init__(self, name, sources, destination, description=None, callbacks=[]):
        '''
        @param name: the state event name
        @param sources: the source states from which destination state is eligible
        @param destination: the destination state
        @param callbacks: collection of callbacks to invoke on this event (TODO)
        '''
        self.__id = id(self)
        self.__name = name
        self.__sources = sources
        self.__destination = destination
        self.__description = description
        self.__callbacks = callbacks

    def get_name(self):
        """
        @return: the name of DFSAEvent
        """
        return self.__name

    def get_sources(self):
        """
        @return: the sources of DFSAEvent
        """
        return self.__sources

    def get_destination(self):
        """
        @return: the destination of DFSAEvent
        """
        return self.__destination

    def get_description(self):
        """
        @return: the description of DFSAEvent
        """
        return self.__description

    def get_callbacks(self):
        """
        @return: the destination of DFSAEvent
        """
        return self.__callbacks

    @Requires(types.MethodType)
    def add_callback(self, callback):
        """
        adds new callback to event

        @param callback: the method to register
        """
        if self.__callbacks == None:
            self.__callbacks = []
        self.__callbacks.append(callback)

    def __str__(self):
        return (
            "DFSAEvent: %s\n" + \
            "name: %s\n" + \
            "sources: %s\n" + \
            "destination: %s\n" + \
            "callbacks: %s") % (
                 str(self.__id),
                 self.get_name(),
                 str([
                      str(DFSAState(src))
                      for src in self.get_sources()
                    ]
                 ),
                 str(DFSAState(self.get_destination())),
                 str([str(callback) for callback in self.get_callbacks()])
             )
