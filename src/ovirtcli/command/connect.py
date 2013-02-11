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
from ovirtcli.settings import OvirtCliSettings
from ovirtsdk.infrastructure.errors import RequestError, NoCertificatesError, \
    ConnectionError
from cli.messages import Messages


class ConnectCommand(OvirtCommand):

    name = 'connect'
    description = 'connect to a oVirt manager'
    args_check = (0, 3)

    helptext = """\
        == Usage ==

        connect
        connect <url> <username> <password> [command options]

        == Description ==

        Connect to a oVirt manager. This command has two forms. In the first
        form, no arguments are provided, and the connection details are read
        from their respective configuration variables. In the second form,
        the connection details are provided as arguments.

        The arguments are:

         * url          - The URL to connect to (http[s]://server[:port]/api).
         * username     - The user to connect as. (user@domain).
         * password     - The password to use.
         * [key-file]   - The client PEM key file to use.
         * [cert-file]  - The client PEM certificate file to use.
         * [ca-file]    - The server CA certificate file to use.
         * [filter]     - Enables user permission based filtering.
         * [insecure]   - Allow connecting to SSL sites without certificates.
         * [port]       - The port to use (if not specified in url).
         * [timeout]    - The request timeout.
        """

    def execute(self):
        args = self.arguments
        settings = self.context.settings
        stdout = self.context.terminal.stdout
        context = self.context

        MIN_FORCE_CREDENTIALS_CHECK_VERSION = ('00000003', '00000001', '00000000', '00000004')

        key_file = self.xNoneType(settings.get('ovirt-shell:key_file'))
        cert_file = self.xNoneType(settings.get('ovirt-shell:cert_file'))
        ca_file = self.xNoneType(settings.get('ovirt-shell:ca_file'))
        port = settings.get('ovirt-shell:port')
        timeout = settings.get('ovirt-shell:timeout')
        debug = settings.get('cli:debug')
        insecure = settings.get('ovirt-shell:insecure')
        filter_ = settings.get('ovirt-shell:filter')

        if self.context.connection is not None and \
                self.__test_connectivity() and \
                self.context.status != self.context.COMMUNICATION_ERROR:
            stdout.write(Messages.Warning.ALREADY_CONNECTED)
            return
        if len(args) == 3:
            url, username, password = args
        else:
            url = settings.get('ovirt-shell:url')
            if not url:
                self.error(Messages.Error.MISSING_CONFIGURATION_VARIABLE % 'url')
            username = settings.get('ovirt-shell:username')
            if not username:
                self.error(Messages.Error.MISSING_CONFIGURATION_VARIABLE % 'username')
            password = settings.get('ovirt-shell:password')
            if not password:
                self.error(Messages.Error.MISSING_CONFIGURATION_VARIABLE % 'password')

        try:
            self.context.set_connection (API(url=url,
                                             username=username,
                                             password=password,
                                             key_file=key_file,
                                             cert_file=cert_file,
                                             ca_file=ca_file,
                                             insecure=insecure,
                                             filter=filter_,
                                             port=port if port != -1 else None,
                                             timeout=timeout if timeout != -1 else None,
                                             debug=debug),
                                         url=url)

            if context.sdk_version < MIN_FORCE_CREDENTIALS_CHECK_VERSION:
                self.__test_connectivity()

            self.context.history.enable()
            stdout.write(OvirtCliSettings.CONNECTED_TEMPLATE % \
                         self.context.settings.get('ovirt-shell:version'))

        except RequestError, e:
            self.__cleanContext()
            self.error("[" + str(e.status) + '] - ' + str(e.reason) + ', ' + str(e.detail))
        except NoCertificatesError:
            self.__cleanContext()
            self.error(Messages.Error.NO_CERTIFICATES)
        except ConnectionError, e:
            self.__cleanContext()
            self.context._clean_settings()
            self.error(str(e))
        except Exception, e:
            self.__cleanContext()
            self.error(str(e))
        finally:
            # do not log connect command details as it may be
            # a subject for password stealing or DOS attack
            self.__remove_history_entry()

    def __test_connectivity(self):
        return self.context.connection.test(throw_exception=True)

    def __remove_history_entry(self):
        last_entry = self.context.history.get(self.context.history.length() - 1)
        if last_entry and last_entry.startswith(ConnectCommand.name):
            self.context.history.remove(self.context.history.length() - 1)

    def __cleanContext(self):
        if self.context.connection is not None:
            self.context._clean_settings()
            try:
                self.context.connection.disconnect()
            except Exception, e:
                self.error(e.strerror.lower())
        self.context.connection = None

    def xNoneType(self, s):
        return None if s == 'None' else s
