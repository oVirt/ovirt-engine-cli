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


class HelpCommand(Command):

    name = 'help'
    description = 'show help'
    args_check = None
    valid_options = [('*', str)]

    helptext = """\
        == Usage ==

        help
        help <command> [arguments] [options]

        == Description ==

        Show help about a command. If no command is specified, a general help
        section is displayed.
        """

    helptext1 = """\
        == Introduction ==

        Welcome to cli-test. This is a test driver for the python-cli
        command-line interface construction toolkit. You can type any command
        in the interface below.

        == Available Commands ==

          $commands

        Type 'help <command>' for any of these commands to show detailed help.

        == Command Syntax ==

        The general format for each command is:

          <command> [arguments] [options]

        If arguments contain spaces or other reserved characters, you need to
        quote them. You can use single (') and double (") quotes for this. The
        difference between single and double quotes is that within single
        quotes you can't use any single quotes, while in double quotes you can
        use a double quote provided that you escape it with backslash ('\\').

        Options are always in the long form: --option [value]. The value can
        be optional or mandatory, dependng on the command.

        In addition to the basic command form, the following functionality is
        available:

          * You can use the '<', '<<', '>' and '>>' characters to perform
            shell-like redirections to files in the file system.
          * The output of any command can be piped to a shell command with
            the '|' character.
          * Shell commands can be executed by typing a '!' at the beginning
            of a line.
          * Comments start with '#' and end at the end of a line.
          * Newlines can be escaped by putting a '\\' in front of them. This
            works outside as well as within a quoted string.
          * Multiple commands can be entered on a single line by separating
            them with a semicolon (';').

        == Configuration Variables ==

        A numer of configuration variables are defined that allow you to
        customize the way in which ovirt-shell operations. Type 'show' to see a
        list of all configuration variables and their current values.

        == Examples ==

        Show all configuration variables and redirect the output to a file
        'foo.txt':

          $ set > foo.txt

        The following pages through a long help text:

          $ help | less

        The following shows the contents of a file named foo.txt:

          $ !cat foo.txt
        """

    def execute(self):
        args = self.arguments
        stdout = self.context.terminal.stdout
        if len(args) == 0:
            subst = {}
            commands = self.get_commands()
            subst['commands'] = self.format_list(commands, sort=True)
            helptext = self.format_help(self.helptext1, subst)
            stdout.write(helptext)
        else:
            name = args[0]
            args = args[1:]
            opts = [('--help', None)]
            opts += self.options.items()
            command = self.context._create_command(name, args, opts)
            command.run(self.context)
