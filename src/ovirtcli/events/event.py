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


from ovirtcli.annotations.requires import Requires
from ovirtcli.listeners.ilistener import IListener
from ovirtcli.events.abstractevent import AbstractEvent

class Event(AbstractEvent):
    '''
    The event class implementation
    '''

    def __init__(self):
        self.__listeners = []
        self.__id = id(self)

    @Requires(IListener)
    def __iadd__(self, listener):
        """
        adds event IListener

        @param listener: listener to register
        """
        assert listener != None
        self.__listeners.append(listener)
        return self

    @Requires(IListener)
    def __isub__(self, listener):
        """
        removes event IListener

        @param listener: listener to unregister
        """
        assert listener != None
        self.__listeners.remove(listener)
        return self

    def fire(self, *args, **keywargs):
        '''
        event listeners notification

        @param args: a list o args
        @param kwargs: a list o kwargs
        '''
        for listener in self.__listeners:
            listener.onEvent(*args, **keywargs)
