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

from ovirtsdk.utils.parsehelper import ParseHelper


class UpdateCommand(OvirtCommand):

    name = 'update'
    description = 'update an object'
    args_check = 2
    valid_options = [ ('*', str) ]

    helptext0 = """\
        == Usage ==

        update <type> <id> [base identifiers] [attribute options]

        == Description ==

        Update an existing object. This command requires the following
        arguments:

          * type        The type of object to delete.
          * id          The identifier of the object to delete

        == Available Types ==

        The following object types are available:

          $types

        == Base Identifiers ==

        Some objects can only exist inside other objects. For example a disk
        can only exist as part of a virtual machine. In this case you want to
        update such an object, one or more base identifier options need to be
        given to identify the containing object. These options have the form
        --<type>id <id>.

        == Attribute Options ==

        Attribute options specifiy values for attributes of the object that is
        to be updated.

        Type 'help update <type>' to see an overview of which attributes are
        available for a specific type.

        == Examples ==

        This updates a virtual machine with name "myvm":

          $ update vm myvm --name newname --memory 1024

        == Return Values ==

          $statuses
        """

    helptext1 = """\
        == Usage ==

        update <type> <id> [base identifiers] [attribute options]

        == Description ==

        Update an existing object. This command requires the following
        arguments:

          * type        The type of object to delete.
          * id          The identifier of the object to delete

        See 'help create' for generic help on creating objects.

        == Attribute Options ==

        The following options are available for objects with type $type:

          $options

        == Return Values ==

          $statuses
        """

    def execute(self):
        """Execute the "update" command."""
        args = self.arguments
        opts = self.options

#        Trac issue #179: don't set fields that already exist

        if not (TypeHelper.isKnownType(args[0])):
            self.error('no such type: %s' % args[0])

        resource = self.get_object(args[0], args[1], self.resolve_base(opts))
        if resource is None:
            self.error('object does not exist: %s/%s' % (args[0], args[1]))
        elif hasattr(resource, 'update'):
            obj = self.update_object(resource, opts)
            result = obj.update()
        else:
            self.error('object : %s/%s is immutable' % (args[0], args[1]))

        self.context.formatter.format(self.context, result)

    def show_help(self):
        """Show help for "update"."""
        args = self.arguments
        opts = self.options
        connection = self.check_connection()
        subst = {}
        if len(args) < 2:
            helptext = self.helptext0
            types = self.get_singular_types()
            subst['types'] = self.format_list(types)
        elif len(args) == 2:
            info = ParseHelper.getXmlWrapperType(args[0])
            if info is None:
                self.error('no such type: %s' % args[0])
            base = self.resolve_base(opts)
            obj = self.get_object(info, args[1], base=base)
            if obj is None:
                self.error('no such %s: %s' % (args[0], args[1]))
            methods = connection.get_methods(obj)
            if 'PUT' not in methods:
                self.error('type cannot be updated: %s' % args[0])
            helptext = self.helptext1
            subst['type'] = args[0]
#            options = self.get_options(info, 'U')
            options = params_list = self.get_options(method='update', coll=args[0], sub_coll=base)
            subst['options'] = self.format_list(options)
        statuses = self.get_statuses()
        subst['statuses'] = self.format_list(statuses)
        helptext = self.format_help(helptext, subst)
        stdout = self.context.terminal.stdout
        stdout.write(helptext)
