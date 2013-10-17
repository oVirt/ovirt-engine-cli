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
from ovirtcli.infrastructure.settings import OvirtCliSettings
import threading

HISTORY_METAFILE = "~/." + OvirtCliSettings.PRODUCT.lower() + "shellhistory"
TMP_HISTORY_METAFILE = HISTORY_METAFILE + ".tmp"

class HistoryManager(code.InteractiveConsole):
    """ Provides history management capabilities """

    def __init__(self,
                 locals=None,  # @ReservedAssignment
                 filename="<console>",
                 histfile=os.path.expanduser(HISTORY_METAFILE),
                 temp_histfile=os.path.expanduser(TMP_HISTORY_METAFILE),
                 enabled=False):

        readline.set_history_length(3000)
        self.lock = threading.RLock()
        self.enabled = enabled
        self.histfile = histfile
        self.tmp_histfile = temp_histfile
        code.InteractiveConsole.__init__(self, locals, filename)
        if enabled: self.enable()

    def get(self, indx):
        return readline.get_history_item(indx)

    def length(self):
        return readline.get_current_history_length()

    def list(self):
        buff = []
        ln = self.length()
        if ln > 0:
            for i in range(ln):
                if i > 0: buff.append(self.get(i))
        return buff

    def listBetweenIndexes(self, from_indx, to_indx):
        buff = []
        ln = self.length()
        if ln > 0:
            for i in range(from_indx, to_indx):
                if i > 0 and i < ln: buff.append(self.get(i))
        return buff

    def export(self, filename):
        readline.write_history_file(filename)

    def clear(self):
        readline.clear_history()

    def enable(self):
        with self.lock:
            self.enabled = True
            self.__register_file(self.histfile)

    def disable(self):
        with self.lock:
            self.enabled = False
            self.__dump_callback(self.histfile)
            self.__register_file(self.tmp_histfile)
            self.clear()

    def remove(self, entry):
        if self.length() > 0:
            readline.remove_history_item(entry)

    def __unregister_dump_callback(self):
        for item in atexit._exithandlers:
            if hasattr(item[0], 'func_name') and \
               item[0].func_name == '__dump_callback':
                atexit._exithandlers.remove(item)

    def __register_file(self, filename):
        self.__unregister_dump_callback()
        if hasattr(readline, "read_history_file"):
            try:
                readline.read_history_file(filename)
            except IOError:
                pass
            atexit.register(self.__dump_callback, filename)

    def __dump_callback(self, histfile):
        readline.write_history_file(histfile)

