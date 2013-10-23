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

class DFSAEventContext(object):
    '''
    Deterministic Finite-State Automata event context
    '''


    def __init__(self, name, sources, destination, callbacks=[]):
        '''
        @param name: the state event name
        @param sources: the source states from which destination state is eligible
        @param destination: the destination state
        @param callbacks: collection of callbacks to invoke on this event (TODO)
        '''
        self.__id = id(self)
        self.__name = name
        self.__source = sources
        self.__destination = destination

    def get_name(self):
        return self.__name

    def get_sources(self):
        return self.__sources

    def get_destination(self):
        return self.__destination

    def get_callbacks(self):
        return self.__callbacks

    def __str__(self):
        print 'DFSAEventContext: %s\n' + \
              'name: %s\n' + \
              'sources: %s\n' + \
              'destination: %s' % \
              (
               str(self.__id),
               self.get_name(),
               self.get_sources(),
               self.get_destination()
              )
