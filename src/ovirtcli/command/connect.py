
import socket

from ovirtcli.command.command import OvirtCommand

from ovirtsdk.api import API


class ConnectCommand(OvirtCommand):

    name = 'connect'
    description = 'connect to a oVirt manager'
    args_check = (0, 3)

    helptext = """\
        == Usage ==

        connect
        connect <url> <username> <password>

        == Description ==

        Connect to a oVirt manager. This command has two forms. In the first
        form, no arguments are provided, and the connection details are read
        from their respective configuration variables (see 'show'). In
        the second form, the connection details are provided as arguments.

        The arguments are:

         * url          - The URL to connect to.
         * username     - The user to connect as. Important: this needs to be
                          in the user@domain format.
         * password     - The password to use.
        """

    def execute(self):
        args = self.arguments
        settings = self.context.settings
        stdout = self.context.terminal.stdout
        if self.context.connection is not None:
            stdout.write('already connected\n')
            return
        if len(args) == 3:
            url, username, password = args
        else:
            url = settings.get('ovirt-shell:url')
            if not url:
                self.error('missing configuration variable: url')
            username = settings.get('ovirt-shell:username')
            if not username:
                self.error('missing configuration variable: username')
            password = settings.get('ovirt-shell:password')
            if not password:
                self.error('missing configuration variable: password')
#        if settings['cli:verbosity']:
#            level = 10
#        else:
#            level = 1
#        connection.verbosity = level
        try:
            self.context.connection = API(url=url,
                                          username=username,
                                          password=password)
        except socket.error, e:
            self.error(e.strerror.lower())
        except e:
            self.error(str(e))
        stdout.write('connected to oVirt manager at %s\n' % url)
