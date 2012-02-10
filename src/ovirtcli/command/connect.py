#
# Copyright (c) 2010 Red Hat, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#           http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#


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
         * username     - The user to connect as. (format user@domain).
         * password     - The password to use.
         * [key-file]   - The key file to use.
         * [cert-file]  - The certificate file to use.
         * [port]       - The port to use (if not specified in url).
         * [timeout]    - The timeout on request.
        """

    def execute(self):
        args = self.arguments
        settings = self.context.settings
        stdout = self.context.terminal.stdout

        key_file = settings.get('ovirt-shell:key_file')
        cert_file = settings.get('ovirt-shell:cert_file')
        port = settings.get('ovirt-shell:port')
        timeout = settings.get('ovirt-shell:timeout')

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
                                          password=password,
                                          key_file=key_file,
                                          cert_file=cert_file,
                                          port=port,
                                          timeout=timeout)
            self.testConnectivity()
            stdout.write('connected to oVirt manager at %s\n' % url)
        except Exception, e:
            self.__cleanContext()
            self.error(str(e))

    def testConnectivity(self):
        self.context.connection.test()

    def __cleanContext(self):
        if self.context.connection is not None:
            try:
                self.context.connection.disconnect()
            except Exception, e:
                self.error(e.strerror.lower())
        self.context.connection = None
