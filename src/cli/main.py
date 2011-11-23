
import sys
import textwrap
from optparse import OptionParser

from cli.object import create
from cli.context import ExecutionContext
from cli.command import *


class TestContext(ExecutionContext):

    name = 'cli-test'
    welcome = textwrap.dedent("""\
        Welcome to cli-test. This is a test driver for the python-cli.
        Type 'exit' to exit or 'help' for help.
        """)
    goodbye = 'Goodbye!'

    def setup_commands(self):
        """Add commands."""
        self.add_command(SetCommand)
        self.add_command(SaveCommand)
        self.add_command(HelpCommand)
        self.add_command(StatusCommand)
        self.add_command(CdCommand)
        self.add_command(ClearCommand)
        self.add_command(PwdCommand)
        self.add_command(ExitCommand)


def main():
    """Test driver for python-cli."""
    parser = create(OptionParser)
    parser.add_option('-f', '--filter', metavar='FILE',
                      help='execute commands from FILE')
    parser.add_option('-d', '--debug', action='store_true',
                      default=False, help='enable debugging mode')
    parser.add_option('-v', '--verbose', action='store_const',
                      dest='verbosity', default=0, const=10,
                      help='be verbose',)
    opts, args = parser.parse_args()

    if opts.filter:
        try:
            cmdin = file(opts.filter)
        except IOError, e:
            sys.stderr.write('error: %s\n' % e.strerror)
            sys.exit(1)
    else:
        cmdin = sys.stdin

    context = create(TestContext, cmdin)
    context.settings['cli:debug'] = opts.debug
    context.settings['cli:verbosity'] = opts.verbosity

    if len(args) == 0:
        context.execute_loop()
    else:
        command = ' '.join(args) + '\n'
        context.execute_string(command)

    sys.exit(context.status)
