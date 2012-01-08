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


from cli.command.command import Command


class SetCommand(Command):

    name = 'set'
    description = 'set a configuration variable'
    args_check = (0, 2)
    helptext = """\
        == Usage ==

        set
        set <name> <value>

        == Description ==

        Set or show configuration variables. This command has two forms. If
        called without any arguments, it will show a list of all current
        configuration variables. If it is called with a <name> and <value>
        argument, the configuration variable <name> is set to <value>.
        """

    def execute(self):
        args = self.arguments
        settings = self.context.settings
        stdout = self.context.terminal.stdout
        if len(args) == 0:
            names = settings.keys()
            names.sort()
            stdout.write('Current settings:\n\n')
            for name in names:
                stdout.write('  %s = %s\n' % (name, repr(settings[name])))
            stdout.write('\n')
        elif len(args) == 2:
            key, value = args
            try:
                settings[key] = value
            except (KeyError, ValueError), e:
                self.error(e.message)
