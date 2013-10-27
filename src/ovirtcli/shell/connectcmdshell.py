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


import shlex
import sys

from ovirtcli.shell.cmdshell import CmdShell
from ovirtcli.utils.autocompletionhelper import AutoCompletionHelper

class ConnectCmdShell(CmdShell):
    NAME = 'connect'
    OPTIONS = [
       'url',
       'user',
       'password',
       'key-file',
       'cert-file',
       'ca-file',
       'insecure',
       'filter',
       'port',
       'timeout',
       'session-timeout'
    ]

    def __init__(self, context, parser):
        CmdShell.__init__(self, context, parser)

    def __do_verbose_connect(self, context, parser, opts):
        if not self.copy_environment_vars(context):
            sys.exit(1)
        if not self.copy_cmdline_options(opts, context, parser):
            sys.exit(1)
        self.context.execute_string(ConnectCmdShell.NAME + '\n')

    def __do_connect(self, args):
        arg = ConnectCmdShell.NAME + ' ' + args.strip() + '\n'
        self.context.execute_string(arg)

    def do_connect(self, args):
        arg = '--connect ' + args.strip() + '\n'
        m_opts, m_args = self.parser.parse_args(args=shlex.split(arg))

        if m_opts.connect and len(m_args) == 0:
            self.__do_verbose_connect(self.context, self.parser, m_opts)
        else:
            self.__do_connect(args)

    def complete_connect(self, text, line, begidx, endidx):
        return AutoCompletionHelper.complete(line=line, text=text,
                                             args={}.fromkeys(ConnectCmdShell.OPTIONS),
                                             all_options=True)
