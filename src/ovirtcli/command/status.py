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


class StatusCommand(OvirtCommand):

    name = 'status'
    description = 'shows last command status'
    helptext = """\
        == Usage ==

        status

        == Description ==

        Shows the exist status of the last command.
        """

    def execute(self):
        context = self.context
        status = context.status
        if status is not None:
            sstatus = str(status)
            for sym in dir(context):
                if sym[0].isupper() and getattr(context, sym) == status:
                    sstatus += ' (%s)' % sym
        else:
            sstatus = 'N/A'
        self.write(Messages.Info.STATUS % sstatus + '\n')

