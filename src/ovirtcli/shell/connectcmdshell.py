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

from ovirtcli.command.connect import ConnectCommand
from ovirtcli.shell.cmdshell import CmdShell
from ovirtcli.shell.config import Config

class ConnectCmdShell(CmdShell):
    NAME = 'connect'

    def __init__(self, context, parser):
        CmdShell.__init__(self, context, parser)

    def __do_verbose_connect(self, context, parser, opts):
        if not self.copy_environment_vars(context):
            sys.exit(1)
        if not self.copy_cmdline_options(opts, context, parser):
            sys.exit(1)
        self.context.execute_string('connect\n')

        if self.context.status == self.context.OK:
            self.owner.prompt = Config.PROMPT_CONNECTED

    def __do_connect(self, args):
        arg = ConnectCmdShell.NAME + ' ' + args.strip() + '\n'
        self.context.execute_string(arg)

        if self.context.status == self.context.OK:
            self.owner.prompt = Config.PROMPT_CONNECTED

    def do_connect(self, args):
        arg = '--connect ' + args.strip() + '\n'
        m_opts, m_args = self.parser.parse_args(args=shlex.split(arg))

        if m_opts.connect and len(m_args) == 0:
            self.__do_verbose_connect(self.context, self.parser, m_opts)
        else:
            self.__do_connect(args)

    def help_connect(self):
        print ConnectCommand.helptext

    def complete_connect(self, text, line, begidx, endidx):
        connect_args = [ 'url', 'user', 'password', 'key_file', 'cert_file', 'port', 'timeout']
        if not text:
            completions = connect_args[:]
        else:
            completions = [ '--' + f + ' '
                            for f in connect_args
                            if f.startswith(text)
                            ]
        return completions
