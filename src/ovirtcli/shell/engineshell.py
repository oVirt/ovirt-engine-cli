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
from ovirtcli.shell.capabilitiescmdshell import CapabilitiesCmdShell

from cli.command.help import HelpCommand
from cli.messages import Messages
from cli.executionmode import ExecutionMode

from urlparse import urlparse
from ovirtcli.utils.colorhelper import ColorHelper

from ovirtcli.events.event import Event
from ovirtcli.listeners.errorlistener import ErrorListener
from ovirtcli.settings import OvirtCliSettings
from ovirtcli.prompt import PromptMode
from cli.error import CommandError

from ovirtcli.state.statemachine import StateMachine

class EngineShell(cmd.Cmd, ConnectCmdShell, ActionCmdShell, \
                  ShowCmdShell, ListCmdShell, UpdateCmdShell, \
                  RemoveCmdShell, AddCmdShell, DisconnectCmdShell, \
                  ConsoleCmdShell, PingCmdShell, StatusCmdShell, \
                  ClearCmdShell, FileCmdShell, HistoryCmdShell, \
                  InfoCmdShell, SummaryCmdShell, CapabilitiesCmdShell):
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
        CapabilitiesCmdShell.__init__(self, context, parser)

        self.onError = Event()  # triggered when error occurs
        self.onInit = Event()  # triggered on init()
        self.onExit = Event()  # triggered on exit
        self.onPromptChange = Event()  # triggered onPromptChange
        self.onSigInt = Event()  # triggered on SigInt fault

        self.__last_output = ''
        self.__input_buffer = ''
        self.__org_prompt = ''
        self.__last_status = -1

        self.__register_sys_listeners()
        self.__register_dfsm_callbacks()
        self.__init_promt()

        cmd.Cmd.doc_header = self.context.settings.get('ovirt-shell:commands')
        cmd.Cmd.undoc_header = self.context.settings.get('ovirt-shell:misc_commands')
        cmd.Cmd.intro = OvirtCliSettings.INTRO

        readline.set_completer_delims(' ')
        signal.signal(signal.SIGINT, self.__handler)

        self.onInit.fire()

    ############################ SHELL ##################################

    def cmdloop(self, intro=None, clear=True):
        try:
            if clear: self.do_clear('')
            return cmd.Cmd.cmdloop(self, intro)
        except KeyboardInterrupt:
            return self.cmdloop(intro="^C", clear=False)
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
                try:
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
                finally:
                    if self.context.status == \
                       self.context.SYNTAX_ERROR \
                       or \
                       self.context.status == \
                       self.context.COMMAND_ERROR \
                       or \
                       self.context.status == \
                       self.context.UNKNOWN_ERROR:
                        self.onError.fire()
                    elif self.context.status == \
                       self.context.COMMUNICATION_ERROR:
                        self.__last_status = self.context.status
                        self.onError.fire()
                    elif self.context.status == \
                       self.context.AUTHENTICATION_ERROR:
                        self.__last_status = self.context.status
                        self.onError.fire()
                    elif self.__last_status <> -1 and \
                         (
                          self.__last_status == \
                          self.context.COMMUNICATION_ERROR
                          or \
                          self.__last_status == \
                          self.context.AUTHENTICATION_ERROR
                         ):
                        self.owner._set_prompt(
                          mode=PromptMode.Original
                        )
                        self.__last_status = -1

    ########################### SYSTEM #################################

    def __register_dfsm_callbacks(self):
        """
        registers StateMachine events callbacks
        """
        StateMachine.add_callback("disconnected", self.__on_disconnected_callback)
        StateMachine.add_callback("connected", self.__on_connected_callback)
        StateMachine.add_callback("exiting", self.__on_exiting_callback)

    def __on_connected_callback(self, **kwargs):
        """
        triggered when StateMachine.CONNECTED state is acquired
        """
        self.context.history.enable()
        self._print(
           OvirtCliSettings.CONNECTED_TEMPLATE % \
           self.context.settings.get('ovirt-shell:version')
        )

    def __on_disconnected_callback(self, **kwargs):
        """
        triggered when StateMachine.DISCONNECTED state is acquired
        """
        self.context.history.disable()
        self._print(OvirtCliSettings.DISCONNECTED_TEMPLATE)
        self.context.connection = None

    def __on_exiting_callback(self, **kwargs):
        """
        triggered when StateMachine.EXITING state is acquired
        """
        if self.context.connection:
            self.onecmd(
                DisconnectCmdShell.NAME + "\n"
            )

    def __register_sys_listeners(self):
        self.onError += ErrorListener(self)

    def __init_promt(self):
        self._set_prompt(mode=PromptMode.Disconnected)

    def _set_prompt(self, mode=PromptMode.Default):
        self.onPromptChange.fire()
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
            self.prompt = self.__get_disconnected_prompt()
        elif mode == PromptMode.Connected:
            self.prompt = self.__get_connected_prompt()
        elif mode == PromptMode.Unauthorized:
            self.prompt = self.__get_unauthorized_prompt()

    def __get_unauthorized_prompt(self):
        dprompt = self.context.settings.get('ovirt-shell:ps1.unauthorized')
        if self.context.mode != ExecutionMode.SCRIPT \
           and self.context.interactive:
            dprompt = dprompt.replace(
                          "unauthorized",
                          ColorHelper.color(
                                "unauthorized",
                                color_=ColorHelper.RED
                          )
            )
        return dprompt

    def __get_disconnected_prompt(self):
        dprompt = self.context.settings.get('ovirt-shell:ps1.disconnected')
        if self.context.mode != ExecutionMode.SCRIPT \
           and self.context.interactive:
            dprompt = dprompt.replace(
                          "disconnected",
                          ColorHelper.color(
                                "disconnected",
                                color_=ColorHelper.RED
                          )
            )
        return dprompt

    def __get_connected_prompt(self):
        if self.context.settings.get('ovirt-shell:extended_prompt'):
            url = self.context.settings.get('ovirt-shell:url')
            url_obj = urlparse(url)
            if url_obj and hasattr(url_obj, 'hostname'):
                cprompt = self.context.settings.get(
                               'ovirt-shell:ps3.connected'
                          ) % {
                               'host':url_obj.hostname
                }
                if self.context.mode != ExecutionMode.SCRIPT \
                   and self.context.interactive:
                    cprompt = cprompt.replace(
                              "connected@" + url_obj.hostname,
                              ColorHelper.color(
                                    'connected@' + url_obj.hostname,
                                    color_=ColorHelper.GREEN
                              )
                )
                return cprompt

        cprompt = self.context.settings.get('ovirt-shell:ps2.connected')
        if self.context.mode != ExecutionMode.SCRIPT \
           and self.context.interactive:
            cprompt = cprompt.replace(
                              "connected",
                              ColorHelper.color(
                                 "connected",
                                 color_=ColorHelper.GREEN
                               )
        )
        return cprompt


    def __persist_cmd_options(self, opts):
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


    def _get_last_status(self):
        return self.__last_status

    def onecmd_loop(self, s):
        opts, args = self.parser.parse_args()
        del args
        self.__persist_cmd_options(opts)
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
        # this is a custom error, consumer responsibility
        # to filter out duplicate calls on event
        self.onError.fire()
        self.context._handle_exception(CommandError(msg))

    def _print(self, msg):
        self.context._pint_text(msg)

    def __handler(self, signum, frame):
        self.onSigInt.fire()
        raise KeyboardInterrupt

    ############################# COMMANDS #################################

    def do_EOF(self, line):
        """\
        == Usage ==

        Ctrl+D

        == Description ==

        Exists shell by /Ctrl+D/ sequence.

        == Examples ==

        Ctrl+D
        """
        self.onExit.fire()
        StateMachine.exiting()  # @UndefinedVariable
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
        self.onExit.fire()
        StateMachine.exiting()  # @UndefinedVariable
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
        self.__last_output = output

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
        if self.__last_output:
            print line.replace('$out', self.__last_output)
        elif line:
            print line
        else: print self.prompt
