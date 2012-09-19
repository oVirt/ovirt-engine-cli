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


class HistoryCommand(OvirtCommand):

    name = 'history'
    description = 'displaying commands history'
    args_check = (0, 1)
    valid_options = [ ('*', int) ]
    helptext = """\
        == Usage ==

        history [indx]

        or

        recursive search by ctrl+r

        == Description ==

        Displaying commands history

        == Examples ==

        - ctrl+r

        - history

        - history 1

        """

    def execute(self):
        args = self.arguments
        context = self.context
        hformat = '[%d] %s'

        if len(args) > 0:
            indx = args[0]
            try:
                slide = int(indx)
                h_item = context.history.get(slide)
                if h_item:
                    self.write('')
                    self.write(hformat % (slide , str(h_item)))
                    self.write('')
            except Exception, e:
                self.error(str(e))
        else:
            i = 0
            history = context.history.list()
            if history:
                self.write('')
                for item in history:
                    self.write(hformat % (i + 1 , str(item)))
                    i += 1
                self.write('')
