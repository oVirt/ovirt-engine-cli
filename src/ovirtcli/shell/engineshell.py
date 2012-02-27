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
import os
import cmd

from ovirtcli.shell.actioncmdshell import ActionCmdShell
from ovirtcli.shell.connectcmdshell import ConnectCmdShell
from ovirtcli.shell.showcmdshell import ShowCmdShell
from ovirtcli.shell.listcmdshell import ListCmdShell
from ovirtcli.shell.updatecmdshell import UpdateCmdShell
from ovirtcli.shell.deletecmdshell import DeleteCmdShell
from ovirtcli.shell.createcmdshell import CreateCmdShell
from ovirtcli.shell.disconnectcmdshell import DisconnectCmdShell
from ovirtcli.shell.consolecmdshell import ConsoleCmdShell
from ovirtcli.shell.pingcmdshell import PingCmdShell
from ovirtcli.shell.statuscmdshell import StatusCmdShell
from ovirtcli.settings import OvirtCliSettings
from ovirtcli.shell.clearcmdshell import ClearCmdShell

import readline

class EngineShell(cmd.Cmd, ConnectCmdShell, ActionCmdShell, \
                  ShowCmdShell, ListCmdShell, UpdateCmdShell, \
                  DeleteCmdShell, CreateCmdShell, DisconnectCmdShell, \
                  ConsoleCmdShell, PingCmdShell, StatusCmdShell, \
                  ClearCmdShell):
    ############################# INIT #################################
    def __init__(self, context, parser, completekey='tab', stdin=None, stdout=None):
        cmd.Cmd.__init__(self, completekey=completekey, stdin=stdin, stdout=stdout)
        ConnectCmdShell.__init__(self, context, parser)
        ActionCmdShell.__init__(self, context, parser)
        ShowCmdShell.__init__(self, context, parser)
        ListCmdShell.__init__(self, context, parser)
        UpdateCmdShell.__init__(self, context, parser)
        DeleteCmdShell.__init__(self, context, parser)
        CreateCmdShell.__init__(self, context, parser)
        DisconnectCmdShell.__init__(self, context, parser)
        ConsoleCmdShell.__init__(self, context, parser)
        PingCmdShell.__init__(self, context, parser)
        StatusCmdShell.__init__(self, context, parser)
        ClearCmdShell.__init__(self, context, parser)

        cmd.Cmd.prompt = self.context.settings.get('ovirt-shell:ps1.disconnected')
        cmd.Cmd.doc_header = self.context.settings.get('ovirt-shell:commands')
        cmd.Cmd.undoc_header = self.context.settings.get('ovirt-shell:misc_commands')
        cmd.Cmd.intro = OvirtCliSettings.INTRO
        self.last_output = ''

        readline.set_completer_delims(' ')
    ########################### SYSTEM #################################
    def cmdloop(self, intro=None, clear=True):
        try:
            if clear: self.do_clear('')
            return cmd.Cmd.cmdloop(self, intro)
        except KeyboardInterrupt, e:
            self.emptyline()
            return True
        except Exception, e:
            sys.stderr.write('error: %s\n' % str(e))
            return self.cmdloop(intro)

    def emptyline(self):
        print self.prompt

    def onecmd(self, s):
        if not s.startswith('#'):
            return cmd.Cmd.onecmd(self, s)

    def onecmd_loop(self, s):
        opts, args = self.parser.parse_args()
        if opts.connect or len(args) == 0:
            self.do_clear('')
            self.do_connect(s)
            self.cmdloop(clear=False)
        else:
            self.cmdloop()

    def precmd(self, line):
        return cmd.Cmd.precmd(self, line)

    def postcmd(self, stop, line):
        return cmd.Cmd.postcmd(self, stop, line)

    def parseline(self, line):
        ret = cmd.Cmd.parseline(self, line)
        return ret

    def do_EOF(self, line):
        '''Exists shell by ctrl+d, ctrl+c'''
        self.emptyline()
        return True

    def do_exit(self, args):
        '''Exists shell'''
        self.emptyline()
        return True

    def do_help(self, args):
        '''Prints help by command'''
        if not args:
            #cmd.Cmd.do_help(self, args)
            self.context.execute_string('help\n')
        else:
            return self.context.execute_string('help ' + args + '\n')
    ############################# SHELL #################################
    def do_shell(self, line):
        "Runs a shell command ('!' can be used instead of 'shell' command)."
        output = os.popen(line).read()
        print output
        self.last_output = output

    def do_echo(self, line):
        "Prints the input, replacing '$out' with the output of the last shell command output"
        if self.last_output:
            print line.replace('$out', self.last_output)
        elif line:
            print line
        else: print self.prompt
    #####################################################################
