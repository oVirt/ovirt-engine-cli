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

from ovirtcli.infrastructure.options import OvirtCliOptionParser
from ovirtcli.infrastructure.context import OvirtCliExecutionContext
from ovirtcli.infrastructure.object import create
from ovirtcli.shell.engineshell import EngineShell

def main():
    # Parse the command line:
    parser = create(OvirtCliOptionParser)
    opts, args = parser.parse_args()

    # Convert the options to a dictionary, so the rest of the code doesn't
    # have to deal with optparse specifics:
    opts = vars(opts)

    # Create the execution context:
    context = OvirtCliExecutionContext(opts=opts, args=args)

    # Create the command interpreter:
    shell = EngineShell(context)
    shell.onecmd_loop()

if __name__ == '__main__':
    main()
