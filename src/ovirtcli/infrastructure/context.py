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


from cli.command import *
from cli.context import ExecutionContext

from ovirtcli.infrastructure.settings import OvirtCliSettings
from ovirtcli.command import *
from ovirtcli.format import *

from ovirtcli.infrastructure.object import create
import pkg_resources
from ovirtcli.command.info import InfoCommand
from ovirtcli.command.summary import SummaryCommand
from ovirtcli.command.capabilities import CapabilitiesCommand
from ovirtcli.infrastructure.historymanager import HistoryManager


class OvirtCliExecutionContext(ExecutionContext):

    Settings = OvirtCliSettings

    name = '%s-shell' % OvirtCliSettings.PRODUCT.lower()

    REMOTE_ERROR = 10
    NOT_FOUND = 11

    SDK_MODULE_NAME = "ovirt-engine-sdk-python"
    CLI_MODULE_NAME = "ovirt-shell"
    DEFAULT_VERSION = (0, 0, 0, 0)

    def __init__(self, args=None, opts=None):
        super(OvirtCliExecutionContext, self).__init__(args=args, opts=opts)
        self.connection = None
        self.url = None
        self.formatter = create(Formatter, self.settings['ovirt-shell:output_format'])
        self.settings.add_callback('cli:verbosity', self._set_verbosity)
        self.settings.add_callback('ovirt-shell:output_format', self._set_formatter)
        self.product_info = None
        self.sdk_version, self.cli_version, self.backend_version = self.__get_version_info()
        self.history = HistoryManager()
        self.__capabilities = None

    def set_connection(self, connection, url=None):
        self.connection = connection
        self.url = url
        self.__update_backend_metadata()

    def get_capabilities(self):
        """
        Fetches system capabilities

        @return: Capabilities
        """

        # cache capabilities cause it won't change
        # during application lifetime and deserializing
        # this object is pretty expensive.
        if not self.__capabilities:
            self.__capabilities = self.connection.capabilities.list()
        return self.__capabilities

    def __get_version_info(self):
        SNAPSHOT_SUFFIX = '-SNAPSHOT'

        try:
            sdk_version = pkg_resources.parse_version(
                              pkg_resources.get_distribution(self.SDK_MODULE_NAME)
                                           .version.replace(SNAPSHOT_SUFFIX, ''))

            cli_version = pkg_resources.parse_version(
                              pkg_resources.get_distribution(self.CLI_MODULE_NAME)
                                           .version.replace(SNAPSHOT_SUFFIX, ''))

            return sdk_version, cli_version, self.DEFAULT_VERSION
        except:
            return self.DEFAULT_VERSION, self.DEFAULT_VERSION, self.DEFAULT_VERSION

    def _set_verbosity(self, key, value):
        if self.connection is None:
            return
        if value:
            level = 10
        else:
            level = 1
        self.connection.verbosity = level

    def _set_formatter(self, key, value):
        self.formatter = create(Formatter, value)

    def _handle_exception(self, e):
        super(OvirtCliExecutionContext, self)._handle_exception(e)

    def setup_commands(self):
#        self.add_command(SetCommand)
#        self.add_command(SaveCommand)
#        self.add_command(CdCommand)
#        self.add_command(PwdCommand)
        self.add_command(ClearCommand)
        self.add_command(ExitCommand)
        self.add_command(ActionCommand)
        self.add_command(AddCommand)
        self.add_command(ConnectCommand)
        self.add_command(ConsoleCommand)
        self.add_command(RemoveCommand)
        self.add_command(DisconnectCommand)
        self.add_command(HelpCommand)
        self.add_command(ListCommand)
        self.add_command(PingCommand)
        self.add_command(ShowCommand)
        self.add_command(StatusCommand)
        self.add_command(UpdateCommand)
        self.add_command(InfoCommand)
        self.add_command(HistoryCommand)
        self.add_command(SummaryCommand)
        self.add_command(CapabilitiesCommand)

    def __update_backend_metadata(self):
        """Return a dict with prompt variables."""

        version = self.__get_backend_version()
        self.settings['ovirt-shell:version'] = version
        self.backend_version = pkg_resources.parse_version(version)

        return {'version':version}

    def __get_backend_version(self):
        backend_version = self.DEFAULT_VERSION
        if self.connection:
            self.product_info = self.connection.get_product_info()
            if self.product_info:
                version = self.product_info.version
                backend_version = (version.major, version.minor,
                                   version.build_, version.revision)
        return '%s.%s.%s.%s' % backend_version

    def _read_command(self):
        return super(OvirtCliExecutionContext, self)._read_command()

    def _clean_settings(self):
        self.settings['ovirt-shell:url'] = ''
        self.settings['ovirt-shell:username'] = None
        self.settings['ovirt-shell:password'] = None
        self.settings['ovirt-shell:key_file'] = None
        self.settings['ovirt-shell:cert_file'] = None
        self.settings['ovirt-shell:ca_file'] = None
        self.settings['ovirt-shell:insecure'] = False
        self.settings['ovirt-shell:port'] = -1
        self.settings['ovirt-shell:timeout'] = -1
        self.settings['ovirt-shell:session_timeout'] = -1
        self.settings['ovirt-shell:kerberos'] = False
