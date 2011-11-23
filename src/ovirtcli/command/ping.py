
from ovirtcli.command.command import OvirtCommand


class PingCommand(OvirtCommand):

    name = 'ping'
    description = 'test the connection'
    helptext = """\
        == Usage ==

        ping

        == Description ==

        Test the connection to the RHEV manager. This command will go out to
        the RHEV manager and retrieve a remote resource. If it succeeds, you
        know that the URL, username and password are working.
        """

    def execute(self):
        connection = self.check_connection()
        stdout = self.context.terminal.stdout
        try:
            connection.vms.list()
#TODO: support this
#            connection.ping()
#        except Error:
        except Exception:
            stdout.write('error: could NOT reach oVirt manager\n')
        else:
            stdout.write('success: oVirt manager could be reached OK\n')
