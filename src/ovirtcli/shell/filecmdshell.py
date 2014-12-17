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
from cli.executionmode import ExecutionMode


class FileCmdShell(CmdShell):
    NAME = 'file'

    def __init__(self, context):
        CmdShell.__init__(self, context)

    def do_file(self, arg):
        """\
        == Usage ==

        file FILE

        == Description ==

        This command reads commands from the FILE instead of stdin.

        == Examples ==

        file /home/test/script
        """

        try:
            self.context.mode = ExecutionMode.SCRIPT
            with open(arg) as script:
                for line in script:
                    line = self.owner.precmd(line)
                    self.owner.print_line(line)
                    self.owner.onecmd(line)
        except Exception, e:
            self._error(str(e))
        finally:
            self.context.mode = ExecutionMode.SHELL
