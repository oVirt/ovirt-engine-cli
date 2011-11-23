
from ovirtcli.command.command import OvirtCommand


class HelpCommand(OvirtCommand):

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

        Welcome to osh. This program is an interactive command-line
        interface into Red Hat Enterprise Virtualization. You can type any
        command in the interface below.

        == Available Commands ==

          $commands

        Type 'help <command>' for any of these commands to show detailed help.
        The first command you probably want to issue is 'help connect' to
        learn how to connect to a RHEV manager.

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
        customize the way in which osh operations. Type 'show' to see a
        list of all configuration variables and their current values.

        == Environment Variables ==

        The following environment variables are recognized:

          * RHEV_URL        - The URL to connect to, same as --url.
          * RHEV_USERNAME   - The username, same as --username
          * RHEV_PASSWORD   - The password, same as --password.

        == Examples ==

        This example lists all vms, and stores the output in a file 'vms.txt':

        $ list vms > vms.txt
        
        This example lists all nics of a host with name <name>. The output is
        in XML format.

        $ set output_format xml
        $ list nics --vmid <name>
        
        The following command shows the total memory in each VM:

        $ set fields.vms "name,status,memory"
        $ list vms

        The following pages through a long help text.

        $ help | less

        The following shows the contents of a file named foo.txt

        $ !cat foo.txt
        """

    def execute(self):
        args = self.arguments
        opts = self.options
        stdout = self.context.terminal.stdout
        if len(args) == 0:
            subst = {}
            commands = self.get_commands()
            subst['commands'] = self.format_list(commands)
            helptext = self.format_help(self.helptext1, subst)
            stdout.write(helptext)
        else:
            name = args[0]
            args = args[1:]
            opts = opts.items()
            opts += [('--help', None)]
            command = self.context._create_command(name, args, opts)
            command.run(self.context)
