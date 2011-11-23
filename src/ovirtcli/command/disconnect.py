
from ovirtcli.command.command import OvirtCommand


class DisconnectCommand(OvirtCommand):

    name = 'disconnect'
    description = 'disconnect from RHEV manager'
    helptext = """\
        == Usage ==

        disconnect

        == Description ==

        Disconnect an active connection to RHEV manager, if any. This method
        can be called multiple times. It is not an error to disconnect when
        not connected.
        """

    def execute(self):
        stdout = self.context.terminal.stdout
        connection = self.context.connection
        if connection is None:
            stdout.write('not connected\n')
            return
        try:
            connection.close()
        except Exception:
            pass
        stdout.write('disconnected from RHEV manager\n')
        self.context.connection = None
