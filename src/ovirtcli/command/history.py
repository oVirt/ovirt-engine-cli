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

from ovirtcli.shell.historycmdshell import HistoryCmdShell
from ovirtcli.command.command import OvirtCommand


class HistoryCommand(OvirtCommand):

    name = 'history'
    description = 'displaying commands history'
    args_check = (0, 1)
    valid_options = [ (
          '--' + item, int
         )
         for item in HistoryCmdShell.OPTIONS
    ]
    helptext = """\
        == Usage ==

        history [indx]

        or

        history --last n

        or

        history --first n

        or

        recursive search by ctrl+r

        == Description ==

        Displaying commands history

        == Examples ==

        - ctrl+r

        - history

        - history 1

        - history --last 3

        - history --first 3

        """

    def execute(self):
        args = self.arguments
        options = self.options

        if len(args) > 0:
            self.__printHistoryAtIndex(args)
        else:
            if len(options) > 0:
                self.__printPartialHistory(options)
            else:
                self.__printAllHistory()

    def __printAllHistory(self):
        context = self.context
        i = 0
        history = context.history.list()
        if history:
            self.write('')
            for item in history:
                self.__printHistoryItemAtIndex(i + 1, item)
                i += 1
            self.write('')

    def __printHistoryAtIndex(self, args):
        context = self.context
        indx = args[0]
        try:
            slide = int(indx)
            h_item = context.history.get(slide)
            self.write('')
            self.__printHistoryItemAtIndex(slide, h_item)
            self.write('')
        except Exception, e:
            self.error(str(e))

    def __printPartialHistory(self, options):
        context = self.context

        key = options.keys()[0]
        prop = key.replace('--', '')
        val = options[key]

        history_len = context.history.length()
        if history_len:
            history_len -= 1
            slide_len = int(val)
            try:
                if prop == 'last':
                    self.__printHistoryBetweenIndexes(max(0, history_len - slide_len), history_len)
                elif prop == 'first':
                    self.__printHistoryBetweenIndexes(0, min(slide_len, history_len))
            except Exception, e:
                self.error(str(e))

    def __printHistoryBetweenIndexes(self, from_index, to_index):
        context = self.context
        i = from_index
        history = context.history.listBetweenIndexes(from_index + 1, to_index + 1)
        if history:
            self.write('')
            for item in history:
                self.__printHistoryItemAtIndex(i + 1, item)
                i += 1
            self.write('')

    def __printHistoryItemAtIndex(self, slide, h_item):
        hformat = '[%d] %s'
        if h_item:
            self.write(hformat % (slide , str(h_item)))

