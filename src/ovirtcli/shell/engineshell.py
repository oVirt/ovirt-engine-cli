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

from ovirtcli.events.event import Event
from ovirtcli.listeners.errorlistener import ErrorListener
from ovirtcli.infrastructure.settings import OvirtCliSettings
from ovirtcli.shell.promptmode import PromptMode
from cli.error import CommandError

from ovirtcli.state.statemachine import StateMachine
from ovirtcli.state.dfsastate import DFSAState
from ovirtcli.shell.promptmanager import PromptManager

class EngineShell(cmd.Cmd, ConnectCmdShell, ActionCmdShell, \
                  ShowCmdShell, ListCmdShell, UpdateCmdShell, \
                  RemoveCmdShell, AddCmdShell, DisconnectCmdShell, \
                  ConsoleCmdShell, PingCmdShell, StatusCmdShell, \
                  ClearCmdShell, FileCmdShell, HistoryCmdShell, \
                  InfoCmdShell, SummaryCmdShell, CapabilitiesCmdShell):
    OFF_LINE_CONTENT = [ConnectCmdShell.NAME, HelpCommand.name, 'exit', "EOF"]

    ############################# INIT #################################

    def __init__(self, context, completekey='tab', stdin=None, stdout=None):
        cmd.Cmd.__init__(self, completekey=completekey, stdin=stdin, stdout=stdout)
        ConnectCmdShell.__init__(self, context)
        ActionCmdShell.__init__(self, context)
        ShowCmdShell.__init__(self, context)
        ListCmdShell.__init__(self, context)
        UpdateCmdShell.__init__(self, context)
        RemoveCmdShell.__init__(self, context)
        AddCmdShell.__init__(self, context)
        DisconnectCmdShell.__init__(self, context)
        ConsoleCmdShell.__init__(self, context)
        PingCmdShell.__init__(self, context)
        StatusCmdShell.__init__(self, context)
        ClearCmdShell.__init__(self, context)
        FileCmdShell.__init__(self, context)
        HistoryCmdShell.__init__(self, context)
        InfoCmdShell.__init__(self, context)
        SummaryCmdShell.__init__(self, context)
        CapabilitiesCmdShell.__init__(self, context)

        self.__last_output = ''
        self.__input_buffer = ''
        self.__last_status = -1

        self.onError = Event()  # triggered when error occurs
        self.onInit = Event()  # triggered on init()
        self.onExit = Event()  # triggered on exit
        self.onPromptChange = Event()  # triggered onPromptChange
        self.onSigInt = Event()  # triggered on SigInt fault

        self.__prompt_manager = PromptManager(self)

        self.__register_sys_listeners()
        self.__register_dfsm_callbacks()
        self.__init_promt()

        cmd.Cmd.doc_header = self.context.settings.get('ovirt-shell:commands')
        cmd.Cmd.undoc_header = self.context.settings.get('ovirt-shell:misc_commands')
        cmd.Cmd.intro = self.__get_intro()

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
                        self.__set_prompt(mode=PromptMode.Multiline)
                        self.__input_buffer += ' ' + s.replace('\\', '') \
                        if not s.startswith(' ') and self.__input_buffer != ''\
                        else s.replace('\\', '')
                        return
                    elif self.__input_buffer != '' and s != 'EOF':
                        self.__input_buffer += ' ' + s \
                        if not s.startswith(' ') else s
                        s = self.__input_buffer
                        self.__input_buffer = ''
                        self.__set_prompt(mode=PromptMode.Original)
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
                        StateMachine.communication_error()  # @UndefinedVariable
                    elif self.context.status == \
                       self.context.AUTHENTICATION_ERROR:
                        self.__last_status = self.context.status
                        self.onError.fire()
                        StateMachine.unauthorized()  # @UndefinedVariable
                    elif self.__last_status <> -1 and \
                         (
                            (
                                self.__last_status == self.context.COMMUNICATION_ERROR
                                and
                                StateMachine.get_current_state() != DFSAState.COMMUNICATION_ERROR
                            )
                          or \
                            (
                                self.__last_status == self.context.AUTHENTICATION_ERROR
                                and
                                StateMachine.get_current_state() != DFSAState.UNAUTHORIZED
                            )
                         ):
                        self.__set_prompt(
                          mode=PromptMode.Original
                        )
                        self.__last_status = -1

    ########################### SYSTEM #################################
    def __get_intro(self):
        """
        @return: the shell intro
        """
        return self.__produce_screen_adapted_message(
                                      text=OvirtCliSettings.INTRO,
                                      border="+"
        )

    def __produce_screen_adapted_message(self, text, border, newline="\n\n"):
        """
        produces (pretty) screen width adapted message
        
        @param text: text to prin
        @param border: border to use (default is '+')
        @param newline: new line separator
        """
        return self.context.formatter.format_terminal(
                          text=text,
                          border=border,
                          termwidth=self.context.terminal._get_width(),
                          newline=newline
        )

    def __init_promt(self):
        self.__set_prompt(mode=PromptMode.Disconnected)

    def __register_dfsm_callbacks(self):
        """
        registers StateMachine events callbacks
        """
        StateMachine.add_callback(
                      DFSAState.UNAUTHORIZED,
                      self.__on_unauthorized_callback
        )
        StateMachine.add_callback(
                      DFSAState.COMMUNICATION_ERROR,
                      self.__on_communication_error_callback
        )
        StateMachine.add_callback(
                      DFSAState.DISCONNECTED,
                      self.__on_disconnected_callback
        )
        StateMachine.add_callback(
                      DFSAState.CONNECTED,
                      self.__on_connected_callback
        )
        StateMachine.add_callback(
                      DFSAState.EXITING,
                      self.__on_exiting_callback
        )

    def __on_unauthorized_callback(self, **kwargs):
        """
        triggered when StateMachine.UNAUTHORIZED state is acquired
        """
        self.__set_prompt(
            mode=PromptMode.Unauthorized
        )

    def __on_communication_error_callback(self, **kwargs):
        """
        triggered when StateMachine.COMMUNICATION_ERROR state is acquired
        """
        self.__set_prompt(
            mode=PromptMode.Disconnected
        )

    def __on_connected_callback(self, **kwargs):
        """
        triggered when StateMachine.CONNECTED state is acquired
        """
        self.context.history.enable()
        if not self.context.settings.get('ovirt-shell:execute_command'):
            self._print(
               self.__produce_screen_adapted_message(
                             text=OvirtCliSettings.CONNECTED_TEMPLATE,
                             border='=',
                             newline='\n'
               ) % \
               self.context.settings.get('ovirt-shell:version')
            )

        self.__set_prompt(
            mode=PromptMode.Connected
        )

    def __on_disconnected_callback(self, **kwargs):
        """
        triggered when StateMachine.DISCONNECTED state is acquired
        """
        self.context.history.disable()
        if not self.context.settings.get('ovirt-shell:execute_command'):
            self._print(
                "\n" + \
                self.__produce_screen_adapted_message(
                             text=OvirtCliSettings.DISCONNECTED_TEMPLATE,
                             border='=',
                             newline='\n'
               )
            )
        self.__set_prompt(
            mode=PromptMode.Disconnected
        )

    def __on_exiting_callback(self, **kwargs):
        """
        triggered when StateMachine.EXITING state is acquired
        """
        if StateMachine.get_origin_state() != DFSAState.DISCONNECTED \
           and \
           self.context.connection:
            self.do_disconnect('')
        else:
            self.do_echo("\n")  # break shell prompt in to bash shell

    def __register_sys_listeners(self):
        self.onError += ErrorListener(self)

    def __set_prompt(self, mode):
        self.__prompt_manager.set_prompt(mode)

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

    def onecmd_loop(self):
        if self.context.settings.get('cli:autoconnect'):
            self.context._collect_connection_data()
            file = self.context.settings.get('ovirt-shell:file')
            execute_command = self.context.settings.get('ovirt-shell:execute_command')
            if not execute_command:
                self.do_clear('')
            self.do_connect('')
            if file:
                self.do_file(file)
                self.do_exit('')
            elif execute_command:
                self.__execute_command(execute_command)
                self.do_exit('')
            else:
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
        if text.startswith('--'):
            text = text.strip()[2:]
        if state == 0:
            self.current_cmd = None
            self.cmd_line = None
            self.has_cmd_and_entity = False
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
                    entity, args, foo = self.parseline(args)
                    if entity != None and args != None and args != '':
                        self.has_cmd_and_entity = True
                    try:
                        self.current_cmd = cmd
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
                self.cmd_line = line
                self.completion_matches = compfunc(text, line, begidx, endidx)
        try:
            if self.has_cmd_and_entity and text != '' and len(self.completion_matches) == 1:
                retval =  self.completion_matches[state]
                is_parameter = False
                if retval != None and self.current_cmd != None and self.cmd_line != None:
                    evalfunc = getattr(self, 'is_' + self.current_cmd + '_argument')
                    if evalfunc:
                        is_parameter = evalfunc(self.cmd_line, retval)
                if retval != None and is_parameter == True and not retval.startswith('--'):
                    return '--' + retval
            return self.completion_matches[state]
        except IndexError:
            return None

    def _error(self, msg):
        # this is a custom error, consumer responsibility
        # to filter out duplicate calls on event
        self.onError.fire()
        self.context._handle_exception(CommandError(msg))

    def _print(self, msg, file=sys.stdout):  # @ReservedAssignment
        """
        prints message to the output device (default stdout).

        @param msg: text to print
        @param file: output device
        """
        self.context._pint_text(msg, file)

    def __execute_command(self, execute):
        """
        executes command from the command line
        via -E/--execute-command

        @param execute: the command to execute
        """
        self.context.settings['cli:autopage'] = False
        for command in execute.split(';'):
            line = self.precmd(command)
            self.print_line(line)
            self.onecmd(line)

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
