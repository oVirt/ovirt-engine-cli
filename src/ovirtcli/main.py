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

    ############################## MAIN #################################
def main():
    parser = create(OvirtCliOptionParser)
    context = OvirtCliExecutionContext(sys.argv, parser)
    shell = EngineShell(context, parser)

    if len(sys.argv) > 1:
        args = ''
        if len(sys.argv) > 2:
            args = sys.argv[1] + " "
            for item in sys.argv[2:]:
                args += '"' + item + '" '
        else:
            args = ' '.join(sys.argv[1:])
        shell.onecmd_loop(args)
    else:
        shell.onecmd_loop('')
    ########################### __main__ #################################
if __name__ == '__main__':
    main()
    ######################################################################
