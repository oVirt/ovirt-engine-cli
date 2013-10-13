#
# Copyright (c) 2013 Red Hat, Inc.
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


import pkg_resources

from ovirtcli.shell.capabilitiescmdshell import CapabilitiesCmdShell
from ovirtcli.command.command import OvirtCommand

class CapabilitiesCommand(OvirtCommand):

    name = 'capabilities'
    description = 'displaying system capabilities'
    args_check = (0, 1)
    valid_options = [ (
          '--' + item, str
         )
         for item in CapabilitiesCmdShell.OPTIONS
    ]

    helptext = """\
        == Usage ==

        capabilities [command options]

        == Description ==

        Displaying system capabilities.

        == Arguments ==

         * [features] - Lists version features.
        """

    def execute(self):
        """executes "capabilities"."""
        opts = self.options

        for capabilities in self.context.get_capabilities():
            capabilities_version = pkg_resources.parse_version(
               "%s.%s.%s.%s" % (
                        capabilities.major,
                        capabilities.minor,
                        capabilities.version if hasattr(
                               capabilities, 'version'
                        ) else '0',
                        capabilities.revision if hasattr(
                               capabilities, 'revision'
                        ) else '0'
                )
            )

            if  capabilities_version[0] == self.context.backend_version[0] and \
                capabilities_version[1] == self.context.backend_version[1]:
                if '--features' in opts:
                    self.context.formatter.format(
                              self.context,
                              capabilities.features.feature,
                              show_all=True
                    )
                else:
                    # backup and restore unrelevant data to this context
                    # saves deepcopy of the object
                    caps_features = capabilities.features
                    caps_id = capabilities.id

                    capabilities.features = None
                    capabilities.id = None

                    self.context.formatter.format(
                              self.context,
                              capabilities
                    )

                    capabilities.features = caps_features
                    capabilities.id = caps_id

    def show_help(self):
        """Show help for "capabilities"."""

        stdout = self.context.terminal.stdout
        stdout.write(self.helptext)
