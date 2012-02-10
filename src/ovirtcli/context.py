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


import textwrap

from cli.command import *
from cli.context import ExecutionContext


from ovirtcli.settings import OvirtCliSettings
from ovirtcli.command import *
from ovirtcli.format import *
from ovirtcli.object import create


class OvirtCliExecutionContext(ExecutionContext):

    Settings = OvirtCliSettings

    name = 'ovirt-shell'
    welcome = textwrap.dedent("""\
        Welcome to Red Hat Enterprise Virtualization.

        Type:  'help' for help with commands
               'exit' to leave this interactive shell
        """)

    REMOTE_ERROR = 10
    NOT_FOUND = 11

    def __init__(self):
        super(OvirtCliExecutionContext, self).__init__()
        self.connection = None
        self.formatter = create(Formatter, self.settings['ovirt-shell:output_format'])
        self.settings.add_callback('cli:verbosity', self._set_verbosity)
        self.settings.add_callback('ovirt-shell:output_format', self._set_formatter)

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
#        self.add_command(ClearCommand)
        self.add_command(ExitCommand)
        self.add_command(ActionCommand)
        self.add_command(CreateCommand)
        self.add_command(ConnectCommand)
        self.add_command(ConsoleCommand)
        self.add_command(CreateCommand)
        self.add_command(DeleteCommand)
        self.add_command(DisconnectCommand)
#        self.add_command(GetKeyCommand)
        self.add_command(HelpCommand)
        self.add_command(ListCommand)
        self.add_command(PingCommand)
        self.add_command(ShowCommand)
        self.add_command(StatusCommand)
        self.add_command(UpdateCommand)

    def _get_prompt_variables(self):
        """Return a dict with prompt variables."""
        subst = {}
        if self.connection:
            api = self.connection.api()
            version = api.product_info.version
            subst['version'] = '%s.%s' % (version.major, version.minor)
        else:
            subst['version'] = ''
        return subst

    def _set_prompt(self):
        """Update the prompt."""
        if self.connection is None:
            prompt = self.settings['ovirt-shell:ps1.disconnected']
        else:
#            subst = self._get_prompt_variables()
#            prompt = self.settings['ovirt-shell:ps1.connected'] % subst
            prompt = '[oVirt-shell:connected]# '
        self.settings['cli:ps1'] = prompt

    def _read_command(self):
        self._set_prompt()
        return super(OvirtCliExecutionContext, self)._read_command()
