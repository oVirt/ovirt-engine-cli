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


class DFSAState(object):
    DISCONNECTING, DISCONNECTED, CONNECTING, \
    CONNECTED, UNAUTHORIZED, EXITING, COMMUNICATION_ERROR = range(7)

    def __init__(self, Type):
        self.value = Type

    def __str__(self):
        if self.value == DFSAState.DISCONNECTED:
            return 'DISCONNECTED'
        if self.value == DFSAState.CONNECTED:
            return 'CONNECTED'
        if self.value == DFSAState.UNAUTHORIZED:
            return 'UNAUTHORIZED'
        if self.value == DFSAState.EXITING:
            return 'EXITING'
        if self.value == DFSAState.DISCONNECTING:
            return 'DISCONNECTING'
        if self.value == DFSAState.CONNECTING:
            return 'CONNECTING'
        if self.value == DFSAState.COMMUNICATION_ERROR:
            return 'COMMUNICATION_ERROR'

    def __eq__(self, y):
        return self.value == y.value
