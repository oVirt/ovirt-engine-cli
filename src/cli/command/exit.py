
from cli.command.command import Command


class ExitCommand(Command):

    name = 'exit'
    description = 'quit this interactive terminal'
    helptext = """\
        == Usage ==
        
        exit
        
        == Description ==
        
        Quit the interative terminal.
        """

    def execute(self):
        self.context._eof = True
