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


import os

from cli.command.command import Command


class CdCommand(Command):

    name = 'cd'
    alias = ('chdir',)
    description = 'change directory'
    args_check = 1
    helptext = """\
        == Usage ==

        cd <directory>

        == Description ==

        Change the current directory to <directory>.
        """

    def execute(self):
        dirname = self.arguments[0]
        try:
            os.chdir(dirname)
        except OSError, e:
            self.error('%s: %s' % (dirname, e.strerror))
