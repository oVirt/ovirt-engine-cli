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
from ovirtcli.infrastructure.settings import OvirtCliSettings
from ovirtcli.shell.engineshell import EngineShell


class HelpCommand(OvirtCommand):

    name = 'help'
    description = 'show help'
    args_check = None
    valid_options = [('*', str)]

    helptext = """\
        == Usage ==

        help
        help <command> <command attributes> [command options]

        == Description ==

        Show help about a command. If no command is specified, a general help
        section is displayed.
        """

    helptext1 = """\
        == Introduction ==

        Welcome to $product-shell. This program is an interactive command-line
        interface into $product Virtualization. You can type any command in 
        the interface below.

        == Available Commands ==

          $commands

        Type 'help <command>' for any of these commands to show detailed help.
        The first command you probably want to issue is 'help connect' to
        learn how to connect to a oVirt manager.

        == Command Syntax ==

        The general format for each command is:

          help <command> <command attributes> [command options]

        If arguments contain spaces or other reserved characters, you need to
        quote them. You can use single (') and double (") quotes for this. The
        difference between single and double quotes is that within single
        quotes you can't use any single quotes, while in double quotes you can
        use a double quote provided that you escape it with backslash ('\\').

        Options are always in the long form: --option [value]. The value can
        be optional or mandatory, depending on the command, see command help
        for details.

        In addition to the basic command form, the following functionality is
        available:

          * You can use the '<', '<<', '>' and '>>' characters to perform
            shell-like redirections to files in the file system.
          * The output of any command can be piped to a shell command with
            the '|' character.
          * Shell commands can be executed by typing a '!' or 'shell' at the 
            beginning of a line.
          * Comments start with '#' and end at the end of a line.
            
        == Examples ==
        
        See 'SUPPORTED HELP FORMATS' section under each command help.

        == Configuration File ==

        oVirt-Shell can be configured with configuration file, configuration file
        ( ~/.ovirtshellrc) automatically created under your home directory (if not exist)
        at first ovirt-shell execution.
        """

    def execute(self):
        args = self.arguments
        opts = self.options
        stdout = self.context.terminal.stdout
        if len(args) == 0:
            subst = {}
            if self.context.connection is not None:
                commands = self.get_commands()
            else:
                off_line_content = \
                          [ f
                            for f in self.get_commands()
                            if f.split(' ')[0] in  EngineShell.OFF_LINE_CONTENT
                          ]
                commands = off_line_content
            subst['commands'] = self.format_list(commands, sort=True)
            subst['product'] = OvirtCliSettings.PRODUCT
            helptext = self.format_help(self.helptext1, subst)
            stdout.write(helptext)
        else:
            name = args[0]
            args = args[1:]
            opts = opts.items()
            opts += [('--help', None)]
            command = self.context._create_command(name, args, opts)
            command.run(self.context)
