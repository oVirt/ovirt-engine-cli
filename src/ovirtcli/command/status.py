
from ovirtcli.command.command import OvirtCommand

from ovirtsdk.infrastructure import contextmanager


class StatusCommand(OvirtCommand):

    name = 'status'
    description = 'show status'
    helptext = """\
        == Usage ==

        status

        == Description ==

        Show the exist status of the last command and the staus of the
        connection to RHEV manager.
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
        if context.connection:
#FIXME: retrive url via API proxy rather than inner proxy to connections_pool 
            sstatus = 'connected to %s' % contextmanager.get('proxy').get_url()
        else:
            sstatus = 'not connected'
        stdout.write('connection: %s\n' % sstatus)
