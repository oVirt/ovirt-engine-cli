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


from ovirtcli.shell.cmdshell import CmdShell


class HistoryCmdShell(CmdShell):
    NAME = 'history'

    def __init__(self, context, parser):
        CmdShell.__init__(self, context, parser)

    def do_history(self, indx):
        """\
        == Usage ==

        history [indx]

        or 

        recursive search by ctrl+r

        == Description ==

        List/Retrieves executed command/s

        == Examples ==

        - ctrl+r

        - history

        - history 1

        """
        hformat = '[%d] %s'

        if indx:
            try:
                slide = int(indx)
                h_item = self.owner.history.get(slide)
                if h_item:
                    self.owner._print(hformat % (slide , str(h_item)))
            except Exception, e:
                self.owner._error(str(e))
        else:
            i = 0
            history = self.history.list()
            if history:
                for item in history:
                    print hformat % (i , str(item))
                    i += 1
                print ''
