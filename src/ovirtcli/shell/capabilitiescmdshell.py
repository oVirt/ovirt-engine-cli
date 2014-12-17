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


from ovirtcli.shell.cmdshell import CmdShell
from ovirtcli.utils.autocompletionhelper import AutoCompletionHelper


class CapabilitiesCmdShell(CmdShell):
    NAME = 'capabilities'
    OPTIONS = [
       'features'
    ]

    def __init__(self, context):
        CmdShell.__init__(self, context)

    def do_capabilities(self, args):
        return self.context.execute_string(CapabilitiesCmdShell.NAME + ' ' + args + '\n')

    def complete_capabilities(self, text, line, begidx, endidx):
        return AutoCompletionHelper.complete(line=line, text=text,
                                             args={}.fromkeys(CapabilitiesCmdShell.OPTIONS),
                                             all_options=True)

    def is_capabilities_argument(self, line, key):
        return key in CapabilitiesCmdShell.OPTIONS
