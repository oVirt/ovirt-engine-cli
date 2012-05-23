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

import code
import readline
import atexit
import os
from ovirtcli.settings import OvirtCliSettings

HISTORY_METAFILE = "~/." + OvirtCliSettings.PRODUCT.lower() + "-shell.history"

class HistoryManager(code.InteractiveConsole):
    """ Provides history management capabilities """

    def __init__(self, locals=None, filename="<console>",
                 histfile=os.path.expanduser(HISTORY_METAFILE)):
        code.InteractiveConsole.__init__(self, locals, filename)
        self.__init_history(histfile)
        self.histfile = histfile

    def __init_history(self, histfile):
        if hasattr(readline, "read_history_file"):
            try:
                readline.read_history_file(histfile)
            except IOError:
                pass
            atexit.register(self.__register_history_metafile, histfile)

    def __register_history_metafile(self, histfile):
        readline.write_history_file(histfile)

    def get(self, indx):
        return readline.get_history_item(indx)

    def length(self):
        return readline.get_current_history_length()

    def list(self):
        buff = []
        ln = self.length()
        if ln > 0:
            for i in range(ln):
                buff.append(self.get(i))
        return buff

    def export(self, filename):
        readline.write_history_file(filename)

    def clear(self):
        readline.clear_history()
