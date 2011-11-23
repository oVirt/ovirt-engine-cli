
import os
from cli.command.command import Command


class PwdCommand(Command):

    name = 'pwd'
    description = 'print working directory'
    helptext = """\
        == Usage ==

        pwd

        == Description ==
        
        Print the current working directory.
        """

    def execute(self):
        stdout = self.context.terminal.stdout
        stdout.write('%s\n' % os.getcwd())
