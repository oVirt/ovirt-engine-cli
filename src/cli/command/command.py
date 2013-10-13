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


from fnmatch import fnmatch
from cli.error import CommandError
from ovirtcli.format.help import Help
from ovirtcli.utils.methodhelper import MethodHelper
from ovirtcli.utils.multivaluedict import MultiValueDict
from cli.warning import GenericWarning


class Command(object):
    """Base class for all commands."""

    name = None
    aliases = ()
    description = None
    helptext = None
    args_check = 0
    valid_options = [ ('--help', None) ]

    def __init__(self, arguments, options):
        """Constructor."""
        self.arguments = arguments
        self.options = MultiValueDict(options)
        if '--help' in self.options:
            self.mode = 'show_help'
        else:
            self.mode = 'execute'
        if self.mode == 'execute':
            self.check_arguments()
            self.check_options()

    def check_arguments(self):
        """Check arguments for validity."""
        args = self.arguments
        if self.args_check is None:
            argsok = True
        elif isinstance(self.args_check, int):
            argsok = self.args_check == len(args)
        elif callable(self.args_check):
            argsok = self.args_check(args)
        elif isinstance(self.args_check, tuple):
            argsok = len(args) in self.args_check
        if not argsok:
            raise SyntaxError, 'wrong number of arguments, try \'help %s\' for help.' % self.name

    def check_options(self):
        """Check options for validity."""
        for key in self.options:
            for name, validator in self.valid_options:
                if not fnmatch(key, name):
                    continue
                value = self.options[key]
                if validator is None:
                    if value is not None:
                        self.error('option %s takes no argument (provided: %s)' %
                                   (key, value))
                else:
                    try:
                        value = validator(value)
                    except ValueError:
                        self.error('could not validate option %s (provided: %s)' %
                                   (key, value))
                break
            else:
                self.error('unknown option: %s' % key)

    def show_help(self):
        """Show help for the current command."""
        subst = {}
        subst['command'] = self.context.command.name
        commands = self.get_commands()
        subst['commands'] = self.format_list(commands, sort=True)
        statuses = self.get_statuses()
        subst['statuses'] = self.format_list(statuses, sort=True)
        helptext = self.format_help(self.helptext, subst)
        stdout = self.context.terminal.stdout
        stdout.write(helptext)

    def run(self, context):
        """Entry point. This either executes a command or shows help."""
        self.context = context
        if self.mode == 'show_help':
            self.show_help()
        elif self.mode == 'execute':
            self.execute()

    def execute(self, context):
        """Override this method in a subclass."""

    def warning(self, message, **kwargs):
        raise GenericWarning(message, **kwargs)

    def write(self, message):
        self.context.terminal.stdout.write(message + '\n')

    def error(self, message, cls=None, **kwargs):
        """Raise an error. This function does not return. If the user is in
        active mode, an error message is displayed and he will be allowed to
        enter another command."""

        print ''

        if cls is None:
            cls = CommandError
        elif not issubclass(cls, CommandError):
            raise TypeError, 'Expecting a CommandError subclass'
        raise cls(message, **kwargs)

    def format_list(self, lst, bullet='*', indent=0, sort=False):
        """Format a list of items, to be used with format_help()."""
        formatted = []
        for elem in lst:
            line = ' ' * indent
            if bullet and elem.find(MethodHelper.NON_ARG_TEMPLATE) == -1:
                line += bullet + ' '
            line += elem.replace(MethodHelper.NON_ARG_TEMPLATE, '')
            formatted.append(line)
        if sort: formatted = sorted(formatted)
        formatted = '\n'.join(formatted)
        return formatted

    def format_map(self, mp, bullet='*', indent=0, sort=True):
        """Format a list of items, to be used with format_help()."""
        formatted = []
        for elem in mp.keys():
            if sort and mp[elem] and type(mp[elem]) == list: mp[elem] = sorted(mp[elem])
            line = ' ' * indent
            if bullet:
                line += bullet + ' '
            if mp[elem] != None:
                line += elem + ' (contexts: ' + str(mp[elem]) + ')'
            else:
                line += elem
            formatted.append(line)
        if sort: formatted = sorted(formatted)
        formatted = '\n'.join(formatted)
        return formatted

    def format_help(self, text, subst):
        return Help.format(text, subst)

    def get_statuses(self):
        """Return a list of all exist statuses that are defined."""
        result = []
        for sym in dir(self.context):
            if not sym.isupper():
                continue
            value = getattr(self.context, sym)
            if not isinstance(value, int):
                continue
            result.append('%03d (%s)' % (value, sym))
        return result

    def get_commands(self):
        """Return a list of all available commands."""
        commands = []
        for cmd in self.context.commands:
            commands.append('%-16s %s' % (cmd.name, cmd.description))
        return commands
