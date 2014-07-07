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


import re

from ovirtcli.command.command import OvirtCommand
from ovirtsdk.api import API
from ovirtsdk.infrastructure.errors import RequestError, NoCertificatesError, \
    ConnectionError
from cli.messages import Messages
from urlparse import urlparse
from ovirtcli.shell.connectcmdshell import ConnectCmdShell
from ovirtcli.state.statemachine import StateMachine

class ConnectCommand(OvirtCommand):

    name = 'connect'
    description = 'connect to a oVirt manager'
    args_check = (0, len(ConnectCmdShell.OPTIONS))
    valid_options = [ (
          '--' + item, str
         )
         for item in ConnectCmdShell.OPTIONS
    ]

    helptext = """\
        == Usage ==

        connect [command options]

        == Description ==

        Connect to a oVirt manager. This command has two forms. In the first
        form, no arguments are provided, and the connection details are read
        from their respective configuration variables. In the second form,
        the connection details are provided as arguments.

        == Arguments ==

         * url               - The URL to connect to (http[s]://server[:port]/ovirt-engine/api).
         * username          - The user to connect as. (user@domain).
         * password          - The password to use.
         * [key-file]        - The client PEM key file to use.
         * [cert-file]       - The client PEM certificate file to use.
         * [ca-file]         - The server CA certificate file to use.
         * [filter]          - Enables user permission based filtering.
         * [insecure]        - Allow connecting to SSL sites without certificates.
         * [port]            - The port to use (if not specified in url).
         * [timeout]         - The request timeout.
         * [session-timeout] - The authentication session timeout in minutes (positive number).
        """

    def execute(self):
        args = self.arguments
        settings = self.context.settings
        context = self.context

        MIN_FORCE_CREDENTIALS_CHECK_VERSION = ('00000003', '00000001', '00000000', '00000004')

        key_file = self.xNoneType(settings.get('ovirt-shell:key_file'))
        cert_file = self.xNoneType(settings.get('ovirt-shell:cert_file'))
        ca_file = self.xNoneType(settings.get('ovirt-shell:ca_file'))
        port = settings.get('ovirt-shell:port')
        timeout = settings.get('ovirt-shell:timeout')
        session_timeout = settings.get('ovirt-shell:session_timeout')
        renew_session = settings.get('ovirt-shell:renew_session')
        debug = settings.get('cli:debug')
        insecure = settings.get('ovirt-shell:insecure')
        dont_validate_cert_chain = settings.get('ovirt-shell:dont_validate_cert_chain')
        filter_ = settings.get('ovirt-shell:filter')

        if self.context.connection is not None and \
           self.context.status != self.context.COMMUNICATION_ERROR and \
           self.context.status != self.context.AUTHENTICATION_ERROR and \
           self.__test_connectivity():
            self.write(
                   Messages.Warning.ALREADY_CONNECTED
            )
            return
        if len(args) == 3:
            url, username, password = args
        else:
            url = settings.get('ovirt-shell:url')
            if not url:
                self.error(
                       Messages.Error.MISSING_CONFIGURATION_VARIABLE % 'url'
                )
            username = settings.get('ovirt-shell:username')
            if not username:
                self.error(
                       Messages.Error.MISSING_CONFIGURATION_VARIABLE % 'username'
                )
            password = settings.get('ovirt-shell:password')
            if not password:
                self.error(
                   Messages.Error.MISSING_CONFIGURATION_VARIABLE % 'password'
                )

        if not self.is_valid_url(url):
            self.error(
               Messages.Error.INVALID_URL_SEGMENT % url
            )

        try:
            StateMachine.connecting()  # @UndefinedVariable

            self.context.set_connection (
                     API(
                         url=url,
                         username=username,
                         password=password,
                         key_file=key_file,
                         cert_file=cert_file,
                         ca_file=ca_file,
                         insecure=insecure,
                         validate_cert_chain=not dont_validate_cert_chain,
                         filter=filter_,
                         port=port if port != -1 else None,
                         timeout=timeout if timeout != -1 else None,
                         session_timeout=session_timeout if session_timeout != -1 else None,
                         renew_session=renew_session,
                         debug=debug
                     ),
                     url=url
             )

            if context.sdk_version < MIN_FORCE_CREDENTIALS_CHECK_VERSION:
                self.__test_connectivity()

            StateMachine.connected()  # @UndefinedVariable

        except RequestError, e:
            StateMachine.rollback()
            self.__cleanContext()
            if debug:
                self.error("[" + str(e.status) + '] - ' + str(e.reason) + ', ' + str(e.detail))
            else:
                self.error("[" + str(e.status) + '] - ' + str(e.reason))
        except NoCertificatesError:
            StateMachine.rollback()
            self.__cleanContext()
            self.error(Messages.Error.NO_CERTIFICATES)
        except ConnectionError, e:
            StateMachine.rollback()
            self.__cleanContext()
            self.context._clean_settings()
            self.error(str(e))
        except TypeError, e:
            StateMachine.rollback()
            self.__cleanContext()
            option, value, expected = self.__normalize_typeerror(e)
            self.error(
                   Messages.Error.INVALID_ARGUMENT_TYPE % (
                               option,
                               value,
                               expected)
            )
        except Exception, e:
            StateMachine.rollback()
            self.__cleanContext()
            self.error(str(e))
        finally:
            # do not log connect command details as it may be
            # a subject for password stealing or DOS attack
            self.__remove_history_entry()

    def is_valid_url(self, url):
        if url is None:
            return False;
        regex = re.compile(
            r'^(?:http)s?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}|'  # ...or ipv4
            r'\[?[A-F0-9]*:[A-F0-9:]+\]?)'  # ...or ipv6
            r'(?::\d+)?'  # optional port
           , re.IGNORECASE)
        if not regex.search(url):
            return False
        hostname = self.get_hostname(url)
        if not self.hostname_is_ip(hostname):
            return True
        return self.is_valid_ip(hostname)

    def get_hostname(self, url):
        url_obj = urlparse(url)
        return getattr(url_obj, 'hostname')

    def hostname_is_ip(self, hostname):
        regex = re.compile(
                   r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}',
                   re.IGNORECASE
        )
        return regex.search(hostname)

    def is_valid_ip(self, hostip):
        regex = re.compile(
                   r'^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$',
                   re.IGNORECASE
        )
        return regex.search(hostip)

    def __normalize_typeerror(self, exception):
            err = str(exception)
            error = err[1:len(err) - 1]
            error = error.replace("\"", "")
            error = error.replace("'", "")
            splitted = error.split(', ')
            option_value = splitted[0].split('=')
            option = option_value[0].upper()
            value = option_value[1]
            expected = splitted[1]

            return option, value, expected

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
            finally:
                self.context.connection = None

    def xNoneType(self, s):
        return None if s == 'None' else s
