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
import re

from ovirtcli.shell.actioncmdshell import ActionCmdShell
from ovirtcli.shell.connectcmdshell import ConnectCmdShell
from ovirtcli.shell.showcmdshell import ShowCmdShell
from ovirtcli.shell.listcmdshell import ListCmdShell
from ovirtcli.shell.updatecmdshell import UpdateCmdShell
from ovirtcli.shell.removecmdshell import RemoveCmdShell
from ovirtcli.shell.addcmdshell import AddCmdShell
from ovirtcli.shell.disconnectcmdshell import DisconnectCmdShell
from ovirtcli.shell.consolecmdshell import ConsoleCmdShell
from ovirtcli.shell.pingcmdshell import PingCmdShell
from ovirtcli.shell.statuscmdshell import StatusCmdShell
from ovirtcli.shell.clearcmdshell import ClearCmdShell
from ovirtcli.shell.summarycmdshell import SummaryCmdShell
from ovirtcli.shell.filecmdshell import FileCmdShell
from ovirtcli.shell.historycmdshell import HistoryCmdShell
from ovirtcli.shell.infocmdshell import InfoCmdShell

from ovirtcli.settings import OvirtCliSettings
from ovirtcli.prompt import PromptMode

from cli.command.help import HelpCommand
from cli.messages import Messages

from urlparse import urlparse


class EngineShell(cmd.Cmd, ConnectCmdShell, ActionCmdShell, \
                  ShowCmdShell, ListCmdShell, UpdateCmdShell, \
                  RemoveCmdShell, AddCmdShell, DisconnectCmdShell, \
                  ConsoleCmdShell, PingCmdShell, StatusCmdShell, \
                  ClearCmdShell, FileCmdShell, HistoryCmdShell, \
                  InfoCmdShell, SummaryCmdShell):
    OFF_LINE_CONTENT = [ConnectCmdShell.NAME, HelpCommand.name, 'exit', "EOF"]
    ############################# INIT #################################
    def __init__(self, context, parser, completekey='tab', stdin=None, stdout=None):
        cmd.Cmd.__init__(self, completekey=completekey, stdin=stdin, stdout=stdout)
        ConnectCmdShell.__init__(self, context, parser)
        ActionCmdShell.__init__(self, context, parser)
        ShowCmdShell.__init__(self, context, parser)
        ListCmdShell.__init__(self, context, parser)
        UpdateCmdShell.__init__(self, context, parser)
        RemoveCmdShell.__init__(self, context, parser)
        AddCmdShell.__init__(self, context, parser)
        DisconnectCmdShell.__init__(self, context, parser)
        ConsoleCmdShell.__init__(self, context, parser)
        PingCmdShell.__init__(self, context, parser)
        StatusCmdShell.__init__(self, context, parser)
        ClearCmdShell.__init__(self, context, parser)
        FileCmdShell.__init__(self, context, parser)
        HistoryCmdShell.__init__(self, context, parser)
        InfoCmdShell.__init__(self, context, parser)
        SummaryCmdShell.__init__(self, context, parser)

        self.last_output = ''
        self.__input_buffer = ''
        self.__org_prompt = ''
        self.__last_status = -1

        self._set_prompt(mode=PromptMode.Disconnected)
        cmd.Cmd.doc_header = self.context.settings.get('ovirt-shell:commands')
        cmd.Cmd.undoc_header = self.context.settings.get('ovirt-shell:misc_commands')
        cmd.Cmd.intro = OvirtCliSettings.INTRO

        readline.set_completer_delims(' ')
        signal.signal(signal.SIGINT, self.handler)

    ########################### SYSTEM #################################
    def cmdloop(self, intro=None, clear=True):
        try:
            if clear: self.do_clear('')
            return cmd.Cmd.cmdloop(self, intro)
        except Exception, e:
            self._error(str(e))
            return self.cmdloop(intro, clear=False)

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
            elif self.context.connection == None and \
                    command.strip() not in EngineShell.OFF_LINE_CONTENT:
                self._error(Messages.Error.INVALID_COMMAND % command)
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

                result = cmd.Cmd.onecmd(self, s)

                # if communication error occurred, change prompt state
                if self.context.status == self.context.COMMUNICATION_ERROR:
                    self.__last_status = self.context.COMMUNICATION_ERROR
                    self.owner._set_prompt(mode=PromptMode.Disconnected)
                elif self.__last_status == self.context.COMMUNICATION_ERROR:
                    self.__last_status = -1
                    self.owner._set_prompt(mode=PromptMode.Original)

                return result

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
            if not self.__org_prompt and self.prompt != "(Cmd) ":
                self.__org_prompt = self.prompt
            self.prompt = self.context.settings.get('ovirt-shell:ps1.disconnected')
        elif mode == PromptMode.Connected:
            self.prompt = self.__get_connected_prompt()

    def __get_connected_prompt(self):
        if self.context.settings.get('ovirt-shell:extended_prompt'):
            url = self.context.settings.get('ovirt-shell:url')
            url_obj = urlparse(url)
            if url_obj and hasattr(url_obj, 'hostname'):
                return self.context.settings.get(
                       'ovirt-shell:ps3.connected'
                       ) % {
                          'host':url_obj.hostname
                       }
        return self.context.settings.get('ovirt-shell:ps2.connected')


    def __persistCmdOptions(self, opts):
        """
        Overrides config file options with cmdline's.
        """
        if opts:
            for k, v in opts.__dict__.items():
                if v:
                    if self.context.settings.has_key('ovirt-shell:' + k):
                        self.context.settings['ovirt-shell:' + k] = v
                    elif self.context.settings.has_key('cli:' + k):
                        self.context.settings['cli:' + k] = v


    def onecmd_loop(self, s):
        opts, args = self.parser.parse_args()
        del args
        self.__persistCmdOptions(opts)
        if opts.connect or self.context.settings.get('cli:autoconnect'):
            self.do_clear('')
            self.do_connect(s)
            if opts.file:
                cmd.Cmd.intro = None
                self.do_file(opts.file)
            self.cmdloop(clear=False)
        else:
            self.cmdloop()

    def precmd(self, line):
        return cmd.Cmd.precmd(self, self.normalize(line))

    def normalize(self, line):
        normalized = line.lstrip()
        rg = re.compile('((?:[a-z][a-z]+))( )(-)(-)(help)', re.IGNORECASE | re.DOTALL)
        m = rg.search(normalized)
        if m:
            normalized = 'help ' + m.group(1)
        return normalized

    def parseline(self, line):
        ret = cmd.Cmd.parseline(self, line)
        return ret

    def completenames(self, text, *ignored):
        dotext = 'do_' + text
        res = [a[3:] for a in self.get_names() if a.startswith(dotext)]
        if res and len(res) == 1:
            res[0] = res[0] + ' '
        return res

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
                del args, foo
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

    def _error(self, msg):
        sys.stderr.write("\nerror: " + msg + "\n")
        sys.stdout.write("\n")

    def _print(self, msg):
        sys.stdout.write("\n" + msg + "\n")
        sys.stdout.write("\n")

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

        sys.exit(0)

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
                self._error(Messages.Error.INVALID_COMMAND % cmd)
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
