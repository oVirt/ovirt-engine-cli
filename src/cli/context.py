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
import logging
import traceback

import codecs
import cStringIO
from kitchen.text.converters import getwriter
import getpass

from StringIO import StringIO
from subprocess import Popen, PIPE

from cli.error import ParseError, CommandError
from cli.object import create
from cli.settings import Settings
from cli.parser import Parser
from cli.platform import Terminal
from cli import platform
from cli.executionmode import ExecutionMode
from ovirtcli.utils.colorhelper import ColorHelper


class ExecutionContext(object):
    """A CLI execution context."""

    name = None

    OK = 0
    SYNTAX_ERROR = 1
    COMMAND_ERROR = 2
    INTERRUPTED = 3
    UNKNOWN_ERROR = 4
    COMMUNICATION_ERROR = 5
    AUTHENTICATION_ERROR = 6

    Parser = Parser
    Terminal = Terminal
    Settings = Settings

    welcome = None
    goodbye = None

    def __init__(self, cmdin=None, args=None, opts=None):
        """Constructor."""
        self.parameters_cash = {}
        self.cmdin = cmdin or sys.stdin
        self.args = args
        self.commands = []
        self.status = None
        self.mode = ExecutionMode.SHELL
        self.interactive = sys.stdin.isatty() and sys.stdout.isatty() \
                    and self.cmdin is sys.stdin
        self.settings = create(self.Settings, self.name)
        self.parser = create(self.Parser)
        self.terminal = create(self.Terminal)
        self._setup_logging()
        self._load_settings()
        self.setup_commands()
        self.__setup_pager()
        self.__encoding = None

        # Copy the command line options into the settings:
        if opts is not None:
            for name, value in opts.iteritems():
                if value is None:
                    continue
                name = name.replace('-', '_')
                if name in ('debug', 'verbosity'):
                    key = 'cli:%s' % name
                else:
                    key = 'ovirt-shell:%s' % name
                try:
                    self.settings[key] = value
                except KeyError:
                    pass
                except ValueError, e:
                    sys.stderr.write('error: %s\n' % str(e))

    def _setup_logging(self):
        """Configure logging."""
        logger = logging.getLogger()
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter('%(levelname)s: %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        self._logger = logger

    def _collect_connection_data(self):
        try:
            if self.settings['ovirt-shell:url'] == '' and \
            not self.__is_option_specified_in_cli_args('--url')  and \
            not self.__is_option_specified_in_cli_args('-l'):
                self.settings['ovirt-shell:url'] = raw_input('URL: ')
            kerberos = self.settings['ovirt-shell:kerberos'] is True \
                or self.__is_option_specified_in_cli_args('--kerberos')
            if not kerberos:
                if not self.settings['ovirt-shell:username'] and \
                not self.__is_option_specified_in_cli_args('--username') and \
                not self.__is_option_specified_in_cli_args('-u'):
                    self.settings['ovirt-shell:username'] = raw_input('Username: ')
                if not self.settings['ovirt-shell:password']:
                    self.settings['ovirt-shell:password'] = getpass.getpass()
        except KeyboardInterrupt:
            sys.exit('')
        except EOFError:
            sys.exit('')
        finally:
            sys.stdin.flush()

    def __option_error(self, opt):
        from cli.messages import Messages
        sys.exit('\n' + Messages.Error.NO_SUCH_OPTION % opt + '\n')

    def __is_option_specified_in_cli_args(self, optionname):
        if self.args:
            if optionname in self.args: return True
            for item in self.args:
                if item.startswith(optionname + '='):
                    return True
        return False

    def __is_auto_connect(self):
        return (self.args and \
            ('-c' in self.args or '--connect' in self.args)) or \
        self.settings.get('cli:autoconnect')

    def _load_settings(self):
        """Load settings."""
        found, old_format = self.settings.load_config_file()
        if not found:
            self.settings.write_example_config_file()
        elif old_format:
            self.settings.write_config_file()
        self.settings.add_callback('cli:debug', self._set_debug)
        self._set_debug('cli:debug', self.settings['cli:debug'])

    def _set_debug(self, key, value):
        """Enable or disable debugging (callback)."""
        if value:
            level = logging.DEBUG
        else:
            level = logging.INFO
        self._logger.setLevel(level)

    def setup_commands(self):
        """Register the default commands. Override in a subclass."""

    def add_command(self, command):
        """Add an additional command. `command' must implement the Command
        interface."""
        for i in range(len(self.commands)):
            if self.commands[i].name == command.name:
                self.commands[i] = command
                self.parameters_cash[command.name.lower()] = {}
                break
        else:
            self.parameters_cash[command.name.lower()] = {}
            self.commands.append(command)

    def execute_loop(self):
        """Run a read/parse/execute loop until EOF."""
        if self.interactive and self.welcome:
            sys.stdout.write('%s\n' % self.welcome)
        self._eof = False
        while not self._eof:
            command = self._read_command()
            if not command:
                continue
            self.execute_string(command)
        if self.interactive and self.goodbye:
            sys.stdout.write('%s\n' % self.goodbye)

    def execute_string(self, command):
        """Parse and execute a string."""
        try:
            parsed = self.parser.parse(command)
        except EOFError:
            sys.stderr.write('error: incomplete command\n')
            return
        except ParseError, e:
            self.status = self.SYNTAX_ERROR
            sys.stderr.write('error: %s\n' % str(e))
            return
        for command in parsed:
            try:
                self._execute_command(command)
            except Exception, e:
                self._handle_exception(e)
            else:
                self.status = self.OK


    def __error_to_string(self, err):
        """Converts an exception to string and normalizing it."""
        err_patterns = [
            "[ERROR]::",
            "oVirt API connection failure, "
        ]

        err_str = str(err)
        err_str = (
           "\n" if not (
                    err_str.startswith("\n")
                    or
                    err_str.startswith("\r\n")
                )
                else ""
        ) + err_str

        for err_pattern in err_patterns:
            if err_str.find(err_pattern) <> -1:
                err_str = err_str.replace(
                              err_pattern, ""
                          )

        return err_str

    def _handle_exception(self, e):
        from ovirtsdk.infrastructure.errors import \
            RequestError, ConnectionError, AmbiguousQueryError

        """Handle an exception. Can be overruled in a subclass."""
        if isinstance(e, KeyboardInterrupt):
            self.status = self.INTERRUPTED
            sys.stdout.write('\n')
        elif isinstance(e, RequestError):
            if hasattr(e, 'status') and e.status == 401:
                self.status = self.AUTHENTICATION_ERROR
            else:
                self.status = getattr(e, 'status', self.COMMAND_ERROR)
            self.__pint_error(e)
            if hasattr(e, 'help'):
                sys.stderr.write('%s\n' % e.help)
        elif isinstance(e, CommandError) or isinstance(e, AmbiguousQueryError):
            self.status = getattr(e, 'status', self.COMMAND_ERROR)
            self.__pint_error(e)
            if hasattr(e, 'help'):
                sys.stderr.write('%s\n' % e.help)
        elif isinstance(e, SyntaxError):
            self.status = getattr(e, 'status', self.SYNTAX_ERROR)
            self.__pint_error(e)
            if hasattr(e, 'help'):
                sys.stderr.write('%s\n' % e.help)
        elif isinstance(e, ConnectionError):
            self.status = getattr(e, 'status', self.COMMUNICATION_ERROR)
            self.__pint_error(e)
            if hasattr(e, 'help'):
                sys.stderr.write('%s\n' % e.help)
        elif isinstance(e, Warning):
            self.__pint_warning(e)
        else:
            self.status = self.UNKNOWN_ERROR
            if self.settings['cli:debug']:
                sys.stderr.write(traceback.format_exc())
            else:
                self.__pint_error(e, header='UNKNOWN ERROR')

    def __pint_error(self, e, header='ERROR'):
        """
        prints error to stderr

        @param e: exception
        @param header: the error header
        """

        text = self.formatter.format_terminal(
                          text=self.__error_to_string(e).strip(),
                          border='=',
                          termwidth=self.terminal._get_width(),
                          newline="\n",
                          header=header.strip()
        )

        text = ColorHelper.colorize(
                  text,
                  ColorHelper.RED if self.mode != ExecutionMode.SCRIPT
                                     and self.interactive
                                  else None
        )

        sys.stderr.write(text + "\n")

    def __pint_warning(self, e):
        """
        prints warning to stdout

        @param e: exception
        """

        text = self.formatter.format_terminal(
                          text=self.__error_to_string(e).strip(),
                          border='=',
                          termwidth=self.terminal._get_width(),
                          newline="\n",
                          header='WARNING'
        )

        text = ColorHelper.colorize(
                  text,
                  ColorHelper.YELLOW if self.mode != ExecutionMode.SCRIPT
                                        and self.interactive
                                     else None
        )

        sys.stdout.write(text + "\n")

    def _pint_text(self, text, file=sys.stdout):  # @ReservedAssignment
        """
        prints text to output device

        @param text: text to print
        @param file: the output device to fetch encoding from
        """
        encoding = self.__get_encoding(file)
        file.write(
               "\n" +
               text.encode(encoding, "replace") +
               "\n"
        )

    def __get_encoding(self, file):  # @ReservedAssignment
        """
        fetches encoding from the file

        @param file: the output device to fetch encoding from
        """
        if not self.__encoding:
            encoding = getattr(file, "encoding", None)
            if not encoding:
                encoding = sys.getdefaultencoding()
            self.__encoding = encoding
        return self.__encoding

    def _read_command(self):
        """Parse input until we can parse at least one full command, and
        return that input."""
        command = ''
        prompt = self.settings['cli:ps1']
        while True:
            try:
                if self.interactive:
                    line = self.terminal.readline(prompt)
                else:
                    line = self.cmdin.readline()
            except EOFError:
                self._eof = True
                sys.stdout.write('\n')
                return
            except KeyboardInterrupt:
                sys.stdout.write('\n')
                return
            if not line:
                self._eof = True
                sys.stdout.write('\n')
                return
            command += line
            try:
                parsed = self.parser.parse(command)  # @UnusedVariable
            except EOFError:
                prompt = self.settings['cli:ps2']
                continue
            except ParseError, e:
                self.status = self.SYNTAX_ERROR
                sys.stderr.write('error: %s\n' % str(e))
                return
            else:
                break
        return command

    def __setup_pager(self):
        pager = self.settings.get('cli:pager')
        if not pager:
            pager = platform.get_pager()
        self.__pager = pager

    def _execute_command(self, parsed):
        """INTERNAL: execute a command."""
#        if parsed[0] == '!':
#            self._execute_shell_command(parsed[1])
#            return

        # The parser produces a list of parameters that include both the
        # arguments and the options. We need to move them to separate
        # lists to ease later processing. Arguments are plain strings and
        # options are pairs containing the name of the option and the value,
        # so it is easy to separate them checking their type.
        name, parameters, redirections, pipeline = parsed
        args = []
        opts = []
        for parameter in parameters:
            if type(parameter) is str:
                args.append(parameter)
            else:
                opts.append(parameter)

        if self.settings.get('cli:autopage'):
            if pipeline:
                pipeline += '| %s' % self.__pager
            else:
                pipeline = self.__pager
        command = self._create_command(name, args, opts)
        self.command = command
        self._setup_pipeline(pipeline)
        self._setup_io_streams(redirections)
        try:
            command.run(self)
        finally:
            self._restore_io_streams()
            self._execute_pipeline()

    def _execute_shell_command(self, command):
        """INTERNAL: execute a shell command."""
        shell = Popen(command, shell=True)
        retcode = shell.wait()
        if retcode != 0:
            m = 'shell command exited with error'
            raise CommandError(m, status=retcode)

    def _create_command(self, name, args, opts):
        """INTERNAL: instantiate a new command."""
        cls = self._get_command(name)
        if cls is None:
            raise CommandError, 'unknown command: %s' % name
        return cls(args, opts)

    def _get_command(self, name):
        """Return the command class for `name' or None."""
        for cls in self.commands:
            if cls.name == name:
                return cls
            if name in cls.aliases:
                return cls

    def _setup_pipeline(self, pipeline):
        """INTERNAL: set up the pipeline, if any."""
        if not pipeline:
            self._pipeline = None
            return

        self._pipeline = Popen(pipeline, stdin=PIPE, stderr=PIPE, shell=True)
        self._pipeinput = codecs.getwriter("utf8")(cStringIO.StringIO())
        self.terminal.stdout = self._pipeinput

    def _setup_io_streams(self, redirections=[]):
        """INTERNAL: set up standard input/output/error."""
        for type_, arg in redirections:
            if type_ == '<':
                self.terminal.stdin = file(arg)
            elif type_ == '<<':
                self.terminal.stdin = StringIO(arg)
            elif type_ == '>':
                self.terminal.stdout = codecs.open(arg, 'w', 'utf8')
            elif type_ == '>>':
                self.terminal.stdout = codecs.open(arg, 'a', 'utf8')

    def _restore_io_streams(self):
        """INTERNAL: reset IO streams."""
        self.terminal.stdin = sys.stdin
        self.terminal.stdout = getwriter('utf8')(sys.stdout)
        self.terminal.stderr = sys.stderr

    def _execute_pipeline(self):
        """INTERNAL: execute the command pipleine (if any)."""
        if not self._pipeline:
            return
        pipeinput = self._pipeinput.getvalue()
        dummy, stderr = self._pipeline.communicate(pipeinput)
        retcode = self._pipeline.returncode
        if retcode != 0:
            raise CommandError, stderr.rstrip()
