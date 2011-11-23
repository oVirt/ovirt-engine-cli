
import os

from cli.command.command import Command


class CdCommand(Command):

    name = 'cd'
    alias = ('chdir',)
    description = 'change directory'
    args_check = 1
    helptext = """\
        == Usage ==

        cd <directory>

        == Description ==

        Change the current directory to <directory>.
        """

    def execute(self):
        dirname = self.arguments[0]
        try:
            os.chdir(dirname)
        except OSError, e:
            self.error('%s: %s' % (dirname, e.strerror))
