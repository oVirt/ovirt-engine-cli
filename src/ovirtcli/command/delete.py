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
#from ovirtsdk.infrastructure import brokers
#from ovirtcli.utils.methodhelper import MethodHelper
#from ovirtsdk.utils.parsehelper import ParseHelper


class DeleteCommand(OvirtCommand):

    name = 'delete'
    aliases = ('remove',)
    description = 'delete an object'
    args_check = 2
    valid_options = [ ('*', str) ]

    helptext = """\
        == Usage ==
    
        delete <type> <id> [object identifiers] [attribute options]

        == Description ==

        Delete an object. The following arguments are required:

          * type        The type of object to delete
          * id          The object identifier

        Objects can be identified by their name and by their unique id.

        == Supported Help formats ==

        - This help will list all available attribute options for given resource removal
          
          * format      - help delete type
          * example     - help delete storagedomain mydomain

        - This help will list all available attribute options for given subresource removal
          
          * format      - help delete subtype --resourceid
          * example     - help delete disk --vmid iscsi_desktop

        == Available Types ==

        The <type> parameter must be one of the following.

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

        - This example deletes a virtual machine named "myvm"

          $ delete vm myvm

        - This example deletes the disk "disk0" from the virtual machine named "myvm"

          $ delete disk disk0 --vmid myvm
          
        - This example deletes the storagedomain "mydomain" using host named "myhost"

          $ delete storagedomain mydomain --host-id myhost
          
        == Return values ==

        This command will exit with one of the following statuses. To see the
        exit status of the last command, type 'status'.

          $statuses
        """

    helptext1 = """\
        == Usage ==

        delete <type> <id> [object identifiers]

        == Description ==

        Delete an object with type '$type'. See 'help delete' for generic
        help on deleting objects.

        == Attribute Options ==

        The following options are available for objects with type '$type':

          $options

        == Return Values ==

          $statuses
        """

    def execute(self):
        """Execute "delete"."""
        args = self.arguments
        opts = self.options

        if not (TypeHelper.isKnownType(args[0])):
            self.error('no such type: %s' % args[0])

        resource = self.get_object(args[0], args[1], self.resolve_base(opts))
        if resource is None:
            self.error('object does not exist: %s/%s' % (args[0], args[1]))
        elif hasattr(resource, 'delete'):
            result = self.execute_method(resource, 'delete', opts)
        else:
            self.error('object : %s/%s is immutable' % (args[0], args[1]))

        self.context.formatter.format(self.context, result)

    def show_help(self):
        """Show help for "delete"."""
        self.check_connection()
        args = self.arguments
        opts = self.options

        subst = {}
        types = TypeHelper.get_types_containing_method('delete')

        subst['types'] = self.format_map(types)
        statuses = self.get_statuses()
        subst['statuses'] = self.format_list(statuses)

        if len(args) == 2 and self.is_supported_type(types.keys(), args[0]):
            base = self.resolve_base(self.options)
            obj = self.get_object(args[0], args[1], base)
            if obj is None:
                self.error('no such "%s": "%s"' % (args[0], args[1]))
            helptext = self.helptext1
            params_list = self.get_options(method='delete',
                                           resource=obj,
                                           sub_resource=base)
            subst['options'] = self.format_list(params_list)
            subst['type'] = args[0]

        elif len(args) == 1 and len(opts) == 2 and self.is_supported_type(types.keys(), args[0]):
            helptext = self.helptext1

            subst['type'] = args[0]

            options = self.get_options(method='delete',
                                       resource=args[0],
                                       sub_resource=self.resolve_base(self.options))
            subst['options'] = self.format_list(options)
            subst['type'] = args[0]
        else:
            helptext = self.helptext
            if len(args) == 1: self.is_supported_type(types.keys(), args[0])

        helptext = self.format_help(helptext, subst)
        stdout = self.context.terminal.stdout
        stdout.write(helptext)
