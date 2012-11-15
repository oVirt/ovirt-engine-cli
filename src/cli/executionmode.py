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


class ExecutionMode():
    SHELL, SCRIPT, DEFAULT, NOPAGING = range(4)

    def __init__(self, Type):
        self.value = Type

    def __str__(self):
        if self.value == ExecutionMode.SHELL:
            return 'SHELL'
        if self.value == ExecutionMode.SCRIPT:
            return 'SCRIPT'
        if self.value == ExecutionMode.DEFAULT:
            return 'DEFAULT'
        if self.value == ExecutionMode.NOPAGING:
            return 'NOPAGING'

    def __eq__(self, y):
        return self.value == y.value
