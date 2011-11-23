
from cli.command.command import Command


class StatusCommand(Command):

    name = 'status'
    description = 'show status'
    helptext = """\
        == Usage ==

        status

        == Description ==

        Show the exit status of the last command.
        """

    def execute(self):
        context = self.context
        stdout = context.terminal.stdout
        status = context.status
        if status is not None:
            sstatus = str(status)
            for sym in dir(context):
                if sym[0].isupper() and getattr(context, sym) == status:
                    sstatus += ' (%s)' % sym
        else:
            sstatus = 'N/A'
        stdout.write('last command status: %s\n' % sstatus)
