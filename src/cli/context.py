
import sys
import logging
import traceback

from StringIO import StringIO
from subprocess import Popen, PIPE

from cli.error import ParseError, CommandError
from cli.object import create
from cli.settings import Settings
from cli.parser import Parser
from cli.platform import Terminal
from cli import platform


class ExecutionContext(object):
    """A CLI execution context."""

    name = None

    OK = 0
    SYNTAX_ERROR = 1
    COMMAND_ERROR = 2
    INTERRUPTED = 3
    UNKNOWN_ERROR = 4

    Parser = Parser
    Terminal = Terminal
    Settings = Settings

    welcome = None
    goodbye = None

    def __init__(self, cmdin=None):
        """Constructor."""
        self.cmdin = cmdin or sys.stdin
        self.commands = []
        self.status = None
        self.interactive = sys.stdin.isatty() and sys.stdout.isatty() \
                    and self.cmdin is sys.stdin
        self.settings = create(self.Settings, self.name)
        self.parser = create(self.Parser)
        self.terminal = create(self.Terminal)
        self._setup_logging()
        self._load_settings()
        self.setup_commands()

    def _setup_logging(self):
        """Configure logging."""
        logger = logging.getLogger()
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter('%(levelname)s: %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        self._logger = logger

    def _load_settings(self):
        """Load settings."""
        found = self.settings.load_config_file()
        if not found:
            self.settings.write_example_config_file()
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
                break
        else:
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
            sys.stderr.write('error: incomplete command')
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

    def _handle_exception(self, e):
        """Handle an exception. Can be overruled in a subclass."""
        if isinstance(e, KeyboardInterrupt):
            self.status = self.INTERRUPTED
            sys.stdout.write('\n')
        elif isinstance(e, CommandError):
            self.status = getattr(e, 'status', self.COMMAND_ERROR)
            sys.stderr.write('error: %s\n' % str(e))
            if hasattr(e, 'help'):
                sys.stderr.write('%s\n' % e.help)
        else:
            self.status = self.UNKNOWN_ERROR
            if self.settings['cli:debug']:
                sys.stderr.write(traceback.format_exc())
            else:
                sys.stderr.write('unknown error: %s\n' % str(e))

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
                parsed = self.parser.parse(command)
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

    def _execute_command(self, parsed):
        """INTERNAL: execute a command."""
        if parsed[0] == '!':
            self._execute_shell_command(parsed[1])
            return
        name, args, opts, redirections, pipeline = parsed
        if self.settings.get('cli:autopage'):
            pager = self.settings.get('cli:pager', platform.get_pager())
            if pipeline:
                pipeline += '| %' % pager
            else:
                pipeline = pager
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
        self._pipeinput = StringIO()
        self.terminal.stdout = self._pipeinput

    def _setup_io_streams(self, redirections=[]):
        """INTERNAL: set up standard input/output/error."""
        for type, arg in redirections:
            if type == '<':
                self.terminal.stdin = file(arg)
            elif type == '<<':
                self.terminal.stdin = StringIO(arg)
            elif type == '>':
                self.terminal.stdout = file(arg, 'w')
            elif type == '>>':
                self.terminal.stdout = file(arg, 'a')

    def _restore_io_streams(self):
        """INTERNAL: reset IO streams."""
        self.terminal.stdin = sys.stdin
        self.terminal.stdout = sys.stdout
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
