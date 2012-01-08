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


import sys

def create(cls, *args, **kwargs):
    """This is our default constructor. It takes care of instantiating the
    right subclass, and configuring it in the right way."""
    from cli.terminal import Terminal
    from optparse import OptionParser
    if issubclass(cls, Terminal):
        obj = cls(sys.stdin, sys.stdout, sys.stderr, **kwargs)
    elif issubclass(cls, OptionParser):
        obj = cls(*args, **kwargs)
        obj.disable_interspersed_args()
    else:
        obj = cls(*args, **kwargs)
    return obj
