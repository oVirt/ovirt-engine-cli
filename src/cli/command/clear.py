
from cli.command.command import Command


class ClearCommand(Command):

    name = 'clear'
    aliases = ('cls',)
    description = 'clear the screen'
    helptext = """\
        == Usage ==
        
        clear
        
        == Description ==
        
        Clear the screen.
        """

    def execute(self):
        self.context.terminal.clear()
