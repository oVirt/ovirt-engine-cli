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
from ovirtcli.utils.typehelper import TypeHelper

class ListCommand(OvirtCommand):

    name = 'list'
    aliases = ('search',)
    description = 'list or search objects'
    usage = 'list <type> [search]... [options]'
    args_check = lambda self, x: len(x) > 0
    valid_options = [ ('*', str) ]

    helptext = """\
        == Usage ==
    
        list <type> [search]... [object identifiers]

        == Description ==

        List or search for objects of a cetain type. There are two forms. If
        only <type> is provided, all objects of the specified type are
        returned. If a search query is given, it must be a valid oVirt search
        query. In that case objects matching the query are returned.

        == Available Types ==

        The <type> parameter must be one of the following. Note: not all types
        implement search!

          $types

        == Object Identifiers ==

        Some objects can only exist inside other objects. For example, a disk
        can only exist in the content of a virtual machine. In this case, one
        or more object identifier opties needs to be provided to identify the
        containing object.

        An object identifier is an option of the form '--<type>id <id>'. This
        would identify an object with type <type> and id <id>. See the
        examples section below for a few examples.

        == Examples ==

        List all virtual machines:

          $ list vms

        Show only virtual machines that have a name that starts with "vm"

          $ list vms name=vm*

        List all disks by vm_id in virtual machine 'myvm':

          $ list disks --vmid UUID

        == Return values ==

        This command will exit with one of the following statuses. To see the
        exit status of the last command, type 'status'.

          $statuses
        """

# TODO: support this:
#        List all disks by vm_name in virtual machine 'myvm':
#
#          $ list disks --vmname myvm


    def execute(self):
        """Execute "list"."""
        args = self.arguments
        opts = self.options

        if not (TypeHelper.isKnownType(args[0])):
            self.error('no such type: %s' % args[0])

        self.context.formatter.format(self.context,
                                      self.get_collection(args[0],
                                                          args[1:] if len(args) > 1 else [],
                                                          base=self.resolve_base(opts)))

    def show_help(self):
        """Show help for "list"."""
        self.check_connection()
        helptext = self.helptext
        subst = {}
        types = self.get_plural_types()
        subst['types'] = self.format_list(types)
        statuses = self.get_statuses()
        subst['statuses'] = self.format_list(statuses)
        helptext = self.format_help(helptext, subst)
        stdout = self.context.terminal.stdout
        stdout.write(helptext)
