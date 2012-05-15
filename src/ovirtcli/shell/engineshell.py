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
import signal
import readline

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

from cli.command.help import HelpCommand
from ovirtcli.prompt import PromptMode
from ovirtcli.shell.filecmdshell import FileCmdShell

class EngineShell(cmd.Cmd, ConnectCmdShell, ActionCmdShell, \
                  ShowCmdShell, ListCmdShell, UpdateCmdShell, \
                  DeleteCmdShell, CreateCmdShell, DisconnectCmdShell, \
                  ConsoleCmdShell, PingCmdShell, StatusCmdShell, \
                  ClearCmdShell, FileCmdShell):
    OFF_LINE_CONTENT = [ConnectCmdShell.NAME, HelpCommand.name, 'exit', "EOF"]
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
        FileCmdShell.__init__(self, context, parser)

        self._set_prompt(mode=PromptMode.Disconnected)
        cmd.Cmd.doc_header = self.context.settings.get('ovirt-shell:commands')
        cmd.Cmd.undoc_header = self.context.settings.get('ovirt-shell:misc_commands')
        cmd.Cmd.intro = OvirtCliSettings.INTRO

        self.last_output = ''
        self.__input_buffer = ''
        self.__org_prompt = ''

        readline.set_completer_delims(' ')
        signal.signal(signal.SIGINT, self.handler)
    ########################### SYSTEM #################################
    def cmdloop(self, intro=None, clear=True):
        try:
            if clear: self.do_clear('')
            return cmd.Cmd.cmdloop(self, intro)
        except Exception, e:
            sys.stderr.write('error: %s\n' % str(e))
            return self.cmdloop(intro)

    def print_line(self, line):
        print self.prompt + line

    def emptyline(self, no_prompt=False):
        if no_prompt:
            print ''
        else:
            print self.prompt

    def onecmd(self, s):
        if not s.startswith('#'):
            command = s.split(' ')[0]
            if command == '' and not self.__input_buffer:
                pass
            elif self.context.connection == None and command not in EngineShell.OFF_LINE_CONTENT:
                print 'error: command "%s" not valid or not available while not connected.' % command
            else:
                if s.endswith('\\') and s != 'EOF':
                    self._set_prompt(mode=PromptMode.Multiline)
                    self.__input_buffer += ' ' + s.replace('\\', '') \
                    if not s.startswith(' ') and self.__input_buffer != ''\
                    else s.replace('\\', '')
                    return
                elif self.__input_buffer != '' and s != 'EOF':
                    self.__input_buffer += ' ' + s \
                    if not s.startswith(' ') else s
                    s = self.__input_buffer
                    self.__input_buffer = ''
                    self._set_prompt(mode=PromptMode.Original)

                return cmd.Cmd.onecmd(self, s)

    def _set_prompt(self, mode=PromptMode.Default):
        if mode == PromptMode.Multiline:
            if not self.__org_prompt:
                self.__org_prompt = self.prompt
            self.prompt = '> '
        elif mode == PromptMode.Original:
            if self.__org_prompt:
                self.prompt = self.__org_prompt
                self.__org_prompt = ''
        elif mode == PromptMode.Disconnected or mode == PromptMode.Default:
            self.prompt = self.context.settings.get('ovirt-shell:ps1.disconnected')
        elif mode == PromptMode.Connected:
            self.prompt = self.context.settings.get('ovirt-shell:ps2.connected')

    def onecmd_loop(self, s):
        opts, args = self.parser.parse_args()
        if opts.connect or len(args) == 0:
            self.do_clear('')
            self.do_connect(s)
            if opts.file:
                cmd.Cmd.intro = None
                self.do_file(opts.file)
            self.cmdloop(clear=False)
        else:
            self.cmdloop()

    def precmd(self, line):
        return cmd.Cmd.precmd(self, line.lstrip())

    def parseline(self, line):
        ret = cmd.Cmd.parseline(self, line)
        return ret

    def complete(self, text, state):
        content = []
        line = readline.get_line_buffer().lstrip()

        if self.context.connection == None:
            if not line or len(line) == 0:
                content = EngineShell.OFF_LINE_CONTENT
            elif not line.split(' ')[0] in EngineShell.OFF_LINE_CONTENT or \
                 (len(line.split(' ')) > 1 and line.split(' ')[0] == HelpCommand.name):
                content = [ f
                            for f in EngineShell.OFF_LINE_CONTENT
                            if f.startswith(text)
                          ]
                if len(content) == 0: content = None

        return self.__do_complete(text, state, content=content)

    def __get_begidx(self, text):
        indx = 0
        i = 0
        for char in text:
            i += 1
            if char == ' ' and i != (indx + 1):
                indx = i
        return indx

    def __get_endidx(self, text):
        return len(text)

    def __do_complete(self, text, state, content=[]):
        """Return the next possible completion for 'text'"""
        if state == 0:
            if self.__input_buffer != '':
                if not self.__input_buffer.endswith(readline.get_line_buffer()):
                    origline = self.__input_buffer + (' ' + readline.get_line_buffer()) \
                    if not self.__input_buffer.endswith(' ') \
                    else self.__input_buffer + readline.get_line_buffer() + ' '
                else:
                    origline = self.__input_buffer + ' '
                line = origline.lstrip()
                stripped = len(origline) - len(line)
                begidx = self.__get_begidx(origline) - stripped
                endidx = self.__get_endidx(origline) - stripped
            else:
                origline = readline.get_line_buffer()
                line = origline.lstrip()
                stripped = len(origline) - len(line)
                begidx = readline.get_begidx() - stripped
                endidx = readline.get_endidx() - stripped

            if begidx > 0:
                cmd, args, foo = self.parseline(line)
                if cmd == '':
                    compfunc = self.completedefault
                else:
                    try:
                        compfunc = getattr(self, 'complete_' + cmd)
                    except AttributeError:
                        compfunc = self.completedefault
            else:
                compfunc = self.completenames
            if content and len(content) > 0:
                self.completion_matches = content
            elif content == None:
                self.completion_matches = []
            else:
                self.completion_matches = compfunc(text, line, begidx, endidx)
        try:
            return self.completion_matches[state]
        except IndexError:
            return None


    def do_EOF(self, line):
        """\
        == Usage ==

        Ctrl+D

        == Description ==

        Exists shell by /Ctrl+D/ sequence.

        == Examples ==

        Ctrl+D
        """
        self.emptyline(no_prompt=True)
        return True

    def do_exit(self, args):
        """\
        == Usage ==

        exit

        == Description ==

        Exists shell by /exit/ command.

        == Examples ==

        exit
        """

        self.emptyline(no_prompt=True)
        return True

    def do_help(self, args):
        """\
        == Usage ==

        help ...

        == Description ==

        Prints help by command.

        == Examples ==

        help show
        """

        if not args:
            self.context.execute_string('help\n')
        else:
            cmd = args.split(' ')[0]
            if self.context.connection == None and cmd not in EngineShell.OFF_LINE_CONTENT:
                self.context.terminal.stdout.error(\
                   'error: command "%s" not valid or not available while not connected.' % cmd)
            else:
                if hasattr(self, 'do_' + cmd) and getattr(self, 'do_' + cmd).__doc__:
                    self.context.terminal.stdout.write('\n' + getattr(self, 'do_' + cmd).__doc__ + '\n')
                else:
                    return self.context.execute_string('help ' + args + '\n')
    ############################# SHELL #################################
    def do_shell(self, line):
        """\
        == Usage ==

        shell ...

        == Description ==

        Runs a shell command ('!' can be used instead of 'shell' command).

        == Examples ==

        shell ls -la

        or

        ! ls -la
        """

        output = os.popen(line).read()
        print output
        self.last_output = output

    def do_echo(self, line):
        """\
        == Usage ==

        echo

        == Description ==

        Prints the input, replacing '$out' with the output of the last shell command output

        == Examples ==

        echo $out

        or

        echo str
        """

        if self.last_output:
            print line.replace('$out', self.last_output)
        elif line:
            print line
        else: print self.prompt
    ############################## COMMON ################################
    def handler(self, signum, frame):
        self.emptyline(no_prompt=True)
        sys.exit()
