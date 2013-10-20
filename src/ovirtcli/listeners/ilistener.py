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


from abc import ABCMeta, abstractmethod

class IListener(object):
    '''
    The listener interface
    '''

    __metaclass__ = ABCMeta

    @abstractmethod
    def onEvent(self, *args, **kwargs):
        '''
        fired when event is raised

        @param args: a list o args
        @param kwargs: a list o kwargs
        '''
        raise NotImplementedError
