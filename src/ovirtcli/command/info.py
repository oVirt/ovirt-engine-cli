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
from cli.messages import Messages

import sys
from ovirtcli.utils.versionhelper import VersionHelper


class InfoCommand(OvirtCommand):

    name = 'info'
    description = 'shows environment and application components info'
    helptext = """\
        == Usage ==

        info

        == Description ==

        Shows environment and application components info.
        """

    def execute(self):
        context = self.context

        self.write(
               '\n'
               +
               Messages.Info.BACKEND_VERSION
               %
               VersionHelper.to_string(context.backend_version)
        )
        self.write(
               Messages.Info.SDK_VERSION
               %
               VersionHelper.to_string(context.sdk_version)
        )
        self.write(
               Messages.Info.CLI_VERSION
               %
               VersionHelper.to_string(context.cli_version)
        )
        self.write(
               Messages.Info.PYTHON_VERSION
               %
               VersionHelper.to_string((sys.version_info))
               +
               '\n'
        )
        self.write(
               Messages.Info.BACKEND_ENTRY_POINT
               %
               context.url
        )
        self.write('')
