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

from kitchen.text.converters import getwriter


class Terminal(object):
    """Base class for terminal objects."""

    width = None
    height = None

    def __init__(self, stdin, stdout, stderr):
        self.stdin = stdin
        self.stdout = getwriter('utf8')(stdout)
        self.stderr = stderr

    def clear(self):
        raise NotImplementedError

    def set_echo(self, echo):
        raise NotImplementedError

    def readline(self, prompt):
        raise NotImplementedError
